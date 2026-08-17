# 04_GUIA_FIRMWARE.md
**Versión:** 4.0 | **Estado:** Final | **Audiencia:** Desarrolladores de Firmware

---
## 1. Propósito de este Documento
*Este documento centraliza toda la **lógica, requisitos y ejemplos de código para el firmware** de ARES v4.0. Sirve como la guía principal para los desarrolladores de software embarcado.*

---
# 04_GUIA_FIRMWARE.md
**Versión:** 4.0 | **Estado:** Final | **Audiencia:** Desarrolladores de Firmware

---
## 1. Propósito de este Documento
*Este documento centraliza toda la **lógica, requisitos y ejemplos de código para el firmware** de ARES v4.0. Sirve como la guía principal para los desarrolladores de software embarcado.*

---
## 2. Arquitectura de Firmware (v4.0)

La arquitectura se basa en el principio **"IMU-first, GNSS-as-anchor"**. El sensor de movimiento (IMU) es la fuente primaria de verdad para la actividad, y gobierna cuándo deben activarse los componentes de alto consumo como el GNSS y el módem LTE.

### 2.1. Scheduler de Posicionamiento (IMU-driven)
El firmware debe implementar una máquina de estados gestionada por la actividad detectada en la IMU (BMI270).

*   **ESTADO REST (Reposo):**
    *   **Condición:** Sin locomoción detectada por la IMU de forma sostenida.
    *   **Acción:** GNSS y Módem LTE en modo de bajo consumo o apagados.
    *   **Envío:** Heartbeat de estado/batería/calidad de señal cada **10–30 minutos**.

*   **ESTADO WALK (Paseo):**
    *   **Condición:** Locomoción de baja intensidad/estable detectada por la IMU.
    *   **Acción:** El GNSS se activa para obtener un fix cada **30–60 segundos**. La IMU mide la actividad (pasos, cadencia, intensidad) en continuo.
    *   **Envío:** Se envían "batches" de datos de actividad junto con el fix de GNSS.

*   **ESTADO RUN (Carrera):**
    *   **Condición:** Locomoción de alta cadencia/energía detectada por la IMU.
    *   **Acción:** El GNSS se activa para obtener un fix cada **5–10 segundos**.
    *   **Envío:** Similar a WALK, pero con mayor frecuencia.

*   **ESTADO LIVE (Seguimiento en Vivo):**
    *   **Condición:** Activado por el usuario desde la app.
    *   **Acción:** GNSS y LTE en máxima frecuencia para obtener y enviar un fix cada **2–3 segundos**.

*   **ESTADO LOST (Modo Perdido):**
    *   **Condición:** Activado por el usuario.
    *   **Acción:** No se mantiene una frecuencia fija. Se deben usar **ráfagas de 2-4 segundos** activadas por eventos de riesgo (aceleración alta, cercanía a borde de geofence) para optimizar la batería durante la búsqueda.

### 2.2. Envíos "Event-Driven" y Datos en "Batch"
Para optimizar el consumo de la red LTE (el mayor consumidor de energía), el firmware debe:
*   **Acumular métricas de actividad** de la IMU (pasos, cadencia, intensidad, tiempo en cada estado, etc.) en la memoria local.
*   **Enviar estos datos en "batches"** junto con los fixes de GNSS programados por el scheduler.
*   **Disparar envíos adicionales e inmediatos** si detecta eventos de riesgo, como un sprint inesperado, una caída, o la cercanía al borde de una geofence.

### 2.3. Contextos Adicionales de Ahorro
*   **Zona WiFi Segura:** Cuando el dispositivo detecte una red WiFi conocida (ej. "casa"), debe entrar en un estado de reposo similar a REST, con el GNSS y LTE apagados, enviando solo heartbeats periódicos a través de WiFi si es posible.
*   **Modo "Phone-Assist":** (Ver sección 5 para detalles) Si el móvil del dueño está muy cerca (detectado por BLE), el GNSS del collar puede reducir su frecuencia, usando el GPS del móvil como sensor auxiliar.

---
## 3. Control del Sistema de Iluminación (v4)

*Extraído de `Hardwear.txt` y `ARES_HW_V4_Especificacion_Medium_Large.md`*

### 3.1. Configuración de Hardware y PWM
El sistema utiliza 3 canales PWM para controlar los MOSFETs que manejan los LEDs Rojo, Verde y Azul.

**Ejemplo de implementación en Arduino (`.ino`):**
```cpp
// Pines de control para las puertas (gate) de los MOSFETs
#define LED_R_GATE_PIN 16
#define LED_G_GATE_PIN 17
#define LED_B_GATE_PIN 18

// Canales PWM del ESP32
#define PWM_R_CHANNEL 0
#define PWM_G_CHANNEL 1
#define PWM_B_CHANNEL 2

void setup_led_pwm() {
  // Configurar canales PWM a 2kHz para evitar parpadeo visible
  ledcSetup(PWM_R_CHANNEL, 2000, 8); // Canal, Frecuencia, Resolución (8-bit = 0-255)
  ledcSetup(PWM_G_CHANNEL, 2000, 8);
  ledcSetup(PWM_B_CHANNEL, 2000, 8);

  // Asignar pines a los canales PWM
  ledcAttachPin(LED_R_GATE_PIN, PWM_R_CHANNEL);
  ledcAttachPin(LED_G_GATE_PIN, PWM_G_CHANNEL);
  ledcAttachPin(LED_B_GATE_PIN, PWM_B_CHANNEL);
  
  // NOTA: El PCB debe incluir resistencias de 100k Ohm (pull-down) 
  // en cada gate para evitar "ghosting" durante el arranque.
}
```

### 3.2. Calibración de Color y Voltaje
*   **Balance de Blancos:** Para obtener un color blanco puro, es necesario aplicar un factor de corrección, ya que cada color de LED tiene una intensidad lumínica diferente.
    ```cpp
    void set_led_color(int red, int green, int blue) {
      // Aplicar factor de corrección para un blanco puro
      float r_calib = red * 0.60;
      float g_calib = green * 0.90;
      float b_calib = blue * 1.0;

      ledcWrite(PWM_R_CHANNEL, (int)r_calib);
      ledcWrite(PWM_G_CHANNEL, (int)g_calib);
      ledcWrite(PWM_B_CHANNEL, (int)b_calib);
    }
    ```
*   **Compensación por Voltaje:** A medida que la batería se descarga (especialmente por debajo de 3.4V), los LEDs verdes y azules pierden intensidad antes que los rojos. El firmware debe implementar una **tabla de búsqueda (LUT)** que ajuste el `duty cycle` de cada canal PWM para mantener la consistencia del color a diferentes niveles de voltaje.

### 3.3. Modos de Luz
*   **Modo “Encontrar” (Prioridad #1):**
    *   **Comportamiento:** Parpadeo intenso (ej. 1 Hz: 0.5s ON / 0.5s OFF).
    *   **Color Recomendado:** Cian (Verde + Azul) o Blanco para máxima visibilidad.
    *   **Seguridad:** Debe tener un **timeout máximo de 15 minutos** para no agotar la batería.
*   **Modo Notificación/Estado:** Pulsaciones suaves (ej. "latido") a bajo brillo (10-20%) para indicar estados como "conectado" o "buscando GPS".
*   **Modo Batería Baja:** Un patrón de color rojo (fijo o parpadeante) y una reducción del brillo máximo permitido en todos los demás modos.
*   **"Astro-Reloj":** El sensor de luz se ha eliminado. El firmware debe usar la hora local obtenida del GPS para determinar si es de día o de noche y ajustar el brillo máximo automáticamente.

---
## 4. Lógica de Fusión de Sensores (Anti-Fraude y Anti-Falsos Pasos)

Para garantizar la integridad de los datos de actividad, es crucial cruzar la información de la IMU y del GNSS.

### 4.1. Anti-Fraude (Coche vs. Paseo)
*   **Sensor Primario:** **Bosch BMI270.** Se utiliza su clasificador de actividad y su estado estacionario (`isStationary`).
*   **Sensor Secundario:** Velocidad del GPS.
*   **Lógica:** Si la velocidad del GPS es alta (> 25 km/h) pero la IMU reporta un estado estacionario o no registra un patrón de pasos coherente, el firmware debe clasificar ese trayecto como "viaje en vehículo" y no sumar esa distancia a la actividad del perro.

### 4.2. Anti-Falsos Pasos (Rascado / Sacudidas)
*   **Problema:** Movimientos como rascarse o sacudirse pueden generar picos de aceleración que un contador de pasos simple podría interpretar como locomoción.
*   **Solución:** El firmware debe analizar las características de la señal de la IMU (no solo la magnitud).
    *   **Patrón no periódico:** La locomoción (caminar, correr) tiene un patrón rítmico. El rascado o las sacudidas son erráticos y de alta frecuencia. Se debe implementar un filtro o un clasificador en el firmware que descarte estos eventos como "pasos".
    *   **Validación con GNSS:** Si la IMU detecta "pasos" pero el GNSS indica que no ha habido desplazamiento durante un periodo de tiempo, esos pasos deben ser marcados como "dudosos" o descartados.

---
## 5. Modo "Phone-Assist" (Ahorro con Móvil Auxiliar)

### 5.1. Objetivo
Reducir el consumo del GNSS del collar cuando el móvil del propietario está muy cerca, usando el GPS del móvil como un sensor de apoyo.

### 5.2. Lógica de Activación y Funcionamiento
1.  **Detección de Proximidad:** El collar y la app mantienen una conexión BLE. Si la señal (RSSI) es fuerte y estable por debajo de un umbral (ej. < -50 dBm durante > 30 segundos), se considera que están juntos.
2.  **Validación de Fiabilidad:** El modo solo se activa si la app confirma que tiene un fix de GPS fiable y que el móvil está en movimiento (usando la API de actividad del SO). **Nunca se debe confiar ciegamente en los "pasos" del móvil.**
3.  **Modo Ahorro:** Una vez activado, el collar reduce la frecuencia de su propio GNSS (ej. a 1-2 minutos) y confía en la ruta enviada por el móvil. La IMU del collar sigue midiendo la actividad real del perro.
4.  **Fail-Safe:** Si la señal BLE se debilita o la app pierde la fiabilidad de su GPS, el collar debe **volver inmediatamente a su scheduler normal** para garantizar que nunca se pierda la localización. La seguridad (Geofence, Modo Perdido) siempre es prioritaria y nunca debe depender del móvil.

---
## 6. Consideraciones Adicionales

*   **Limpieza de RF:** Opcional pero recomendado. El firmware podría apagar los LEDs momentáneamente durante las ráfagas de transmisión (TX) del módem LTE para minimizar cualquier posible interferencia de radiofrecuencia (EMI).
*   **Estrategia Anti-Brownout:** El firmware debe monitorizar el voltaje de la batería (VBAT) y, si detecta una caída brusca durante una transmisión LTE, debe implementar una lógica para reintentar la transmisión de forma controlada, evitando un bucle de reinicios que agote la batería.
*   **Store & Forward:** Si se pierde la conectividad LTE, el firmware debe almacenar los "batches" de actividad y los fixes de GNSS en la memoria flash interna. Al recuperar la conexión, debe enviar los datos almacenados para rellenar los huecos en el historial del usuario.
