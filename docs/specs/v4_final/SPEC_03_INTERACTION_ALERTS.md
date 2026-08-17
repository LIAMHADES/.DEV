# SPEC_03: Interacción, Luces y Feedback (ARES v4.0)

**Objetivo**: Definir cómo el usuario interactúa activamente con el dispositivo para localizar al perro o recibir feedback.

## 1. Sistema de Luces (LUZ_ACTIVE)

Control de los 12 LEDs RGB para visibilidad y localización local.

### 1.1. Modos de Luz

1.  **Modo VISIBILIDAD (Paseo Nocturno)**
    - _Propósito_: Que el perro sea visto (seguridad vial).
    - _Patrón_: Fijo o Parpadeo lento (Blink).
    - _Color_: Configurable (Rojo, Verde, Azul, Blanco, Disco).
    - _Timeout_: 15 / 30 min (seguridad batería).
2.  **Modo ENCONTRAR (Búsqueda)**
    - _Propósito_: Localizar el dispositivo perdido en la oscuridad/matorrales.
    - _Patrón_: Flash Estroboscópico (Rápido y Máximo Brillo en pulsos cortos).
    - _Color_: Blanco o Cian (máxima visibilidad).

### 1.2. Reglas de Seguridad (Protección Batería)

- **Bloqueo Crítico**: Si batería < 15%, se **deniega** el encendido de luces (o se permite solo 30 segundos). La prioridad es el GPS.
- **Interferencia RF**: El firmware debe apagar (blanking) los LEDs durante los milisegundos que el módem LTE transmite a máxima potencia, para evitar ruido en la alimentación.

## 2. Buscador Cercano (Find Nearby - BLE)

Uso de Bluetooth Low Energy para la "última milla".

- **Advertising**: El dispositivo hace broadcast BLE periódico (intervalo según modo).
- **App "Hot/Cold"**:
  - Lectura de RSSI (Intensidad de señal).
  - Visualización: Barra que se llena "Frío... Tibio... Caliente...".
- **Acción Local**: Botón en pantalla "Hacer parpadear" (envío comando BLE inmediato `BLINK_NOW`).

## 3. Override Manual ("Forzar Seguimiento")

Botón de pánico/urgencia en la App.

1.  **Usuario**: Pulsa "Rastrear AHORA".
2.  **Backend**:
    - Envía comando `CMD_LIVE_MODE_ON`.
    - Canales: MQTT/Downlink (si conectado) + SMS (si implementado/necesario como fallback extremo, pero v4 prioriza datos) + Notificación Push (si app abierta).
    - _Nota_: Si el dispositivo está durmiendo (Deep Sleep), puede tardar hasta su próximo ciclo de despertar. _Expectativa de usuario_: Explicar "Despertando dispositivo... (puede tardar X min)".
3.  **Dispositivo**:
    - Recibe comando.
    - Pasa a **Modo LIVE** (GPS continuo).
    - Inicia temporizador de seguridad (10 min).
4.  **Confirmación**: App muestra "Dispositivo EN LÍNEA - Actualizando cada 5s".
