# 02_ESPECIFICACION_TECNICA.md
**Versión:** 4.0 | **Estado:** Final | **Audiencia:** Ingenieros de Hardware, Desarrolladores de Firmware

---
## 1. Propósito de este Documento
*Este documento es la **especificación técnica maestra y definitiva** para el hardware de ARES v4.0 (modelos Medium y Large). Consolida todas las decisiones de diseño, componentes, arquitectura y análisis de rendimiento en una única fuente de verdad.*

---
## 2. Funciones Generales Requeridas

*Extraído de `funciones.txt` y actualizado a v4.0*

#### **2.1. POSICIONAMIENTO Y ACTIVIDAD (ARQUITECTURA v4.0)**
```
[OK]  **Actividad Fiable (IMU-first)** → Pasos/cadencia/intensidad medidos por IMU (BMI270)
[OK]  **Precisión objetivo <1m (GNSS como ancla), pendiente de validación de campo** → GNSS calibra y corrige la deriva del IMU
[OK]  **Cobertura global** → LTE Cat-M1 + 2G fallback (SIM7000G)
[OK]  **Live tracking inteligente (Scheduler)** → Frecuencia de envío basada en estados (REST, WALK, RUN, LIVE)
[OK]  **Anti-multipath y Anti-fraude** → Fusión de datos IMU+GNSS para filtrar saltos y movimientos falsos (coche)
```

#### **2.2. MODOS DE FUNCIONAMIENTO (IMU-DRIVEN)**
```
[OK]  **REST/WALK/RUN auto-detect** → El IMU determina el estado y ajusta la frecuencia de GNSS/LTE
[OK]  **Caída/inmovilidad** → Alertas urgentes basadas en IMU
[OK]  **Valla adaptativa ("Near Boundary")** → Aumento de frecuencia de envío al acercarse al borde
[OK]  **Reposo automático (Deep Sleep)** → El IMU detecta inmovilidad prolongada (>2min) para ahorro máximo
[OK]  **Modo "Phone-Assist"** → El móvil cercano por BLE puede reducir el uso de GNSS del collar
```

#### **2.3. GESTIÓN ENERGÍA OPTIMIZADA**
```
[OK]  **Autonomía flexible** → Packs de batería intercambiables
[OK]  **Carga Magnética externa** → Cómoda y 100% impermeable
[OK]  **Protección térmica** → NTC >45°C pausa
[OK]  **Modos deepsleep** → <15uA reposo
[OK]  **Batería modular** → **~2750mAh (Medium) / ~4000mAh (Large)**
```

#### **2.4. COMUNICACIÓN MULTI-NIVEL**
```
[OK]  **LTE+GNSS primario** → Posición mundial y datos de actividad
[OK]  **BLE** → Búsqueda cercana y modo "Phone-Assist"
[OK]  **WiFi** → Detección de zonas seguras (ahorro de energía) y actualizaciones OTA
[OK]  **Conectividad Global (1NCE)** → Estrategia dual Nano-SIM/MFF2
```

#### **2.5. FEEDBACK VISUAL (Sistema v4)**
```
[OK]  **LEDs analógicos RGB (12x 1206)** → Batería/GPS/conexión
[OK]  **Sin sensor de luz** → Control por software (Astro-Reloj)
```

#### **2.6. MONITORIZACIÓN AMBIENTAL**
```
[OK]  **Temperatura ambiente** → Índice calor perro
[OK]  **IP68 resistente** → Sumergible, lluvia/trail/bosque
[OK]  **IK10 Golpes** → Carcasa PC/ABS
```

---
## 3. Arquitectura y Componentes (BOM)

*Extraído y consolidado de `Hardwear.txt` y `funciones.txt`*

### 3.1. Arquitectura Modular v4.0
*   **Carcasa Unificada (Huella Interna):** 36x58 mm.
*   El Módulo Chip es idéntico para ambos modelos. La única variable es el grosor del Módulo Batería.

┌─────────────────────────────┐    CONECTOR    ┌─────────────────────────────┐
│ **MÓDULO A: CEREBRO**       │◄──RAIL──►│ **MÓDULO B: POWER PACK**    │
│ 36x58mm (huella)            │ POGO     │ • Batería LiPo (2750/4000mAh)│
│ • LilyGo, BMI270, Ignion    │ POGO     │ • BQ24040 (Gestión Carga)   │
│ • Conectividad 1NCE (Nano-SIM/MFF2)│          │ • **Contactos Carga Magnética** |
│ • LEDs de control           │          │   (Externos, IP68)          │
└──────────4+4 PADS ORO───────┘          └───────Rail cola milano───────┘
           ↑ O-RING silicona IP68 3ATM ↑

### 3.2. BOM Final (Lista de Materiales)
**Coste total objetivo: ~64-67€**

**MÓDULO CHIP 37x28mm (~43.9€):**
| Componente | Función | Precio Est. |
|---|---|---|
| **LilyGo T-SIM7000G S3**| CPU+GPS <1m+LTE-M | 28€ |
| **Bosch BMI270**| **Sensor Primario de Actividad (IMU)** | 3.2€ |
| **Ignion A101 + LNA**| Antena GPS/LTE (objetivo <1m, pendiente de validar en campo) | 3.2€ |
| Conectividad (1NCE)| Nano-SIM (prototipo) o MFF2 (producción) | ~3€ |
| **12x LEDs SMD 1206**| Feedback visual | 1€ |
| **3x MOSFETs (AO3400A)**| Control de Luces | 1€ |
| **NTC 10kΩ**| Protección térmica | - |
| Resistencias Varias| Pull-down/limit | 0.5€ |
| PCB 4 capas| Conexiones estables | 4€ |

**MÓDULO BATERÍA (~13.5€ + Batería):**
| Componente | Función | Precio Est. |
|---|---|---|
| **BQ24040 TI**| Carga inteligente | 4€ |
| **Conector Magnético IP68**| Carga Externa | 5€ |
| Pogo Pins Oro | Conexión modular | 1.5€ |
| PCB + Rail O-RING | Estructura y sellado | 3€ |
| **Batería LiPo 3.7V**| Energía principal | ~6.5-9.5€ |

---
## 4. Especificaciones Detalladas por Subsistema

### 4.1. Arquitectura de Posicionamiento y Actividad (v4.0)

La estrategia v4.0 se basa en el principio **"IMU-first, GNSS-as-anchor"**. El objetivo es medir la actividad de forma fiable y continua con el mínimo consumo, usando el GNSS solo cuando aporta valor de corrección o para el modo LIVE.

#### 4.1.1. Scheduler de Posicionamiento (IMU-driven)
El firmware opera con una máquina de estados gobernada por la actividad detectada en la IMU (BMI270).

*   **ESTADO REST (Reposo):**
    *   **Condición:** Sin locomoción detectada.
    *   **Acción:** GNSS y Módem LTE en modo de bajo consumo o apagados.
    *   **Envío:** Heartbeat de estado/batería cada **10–30 minutos**.

*   **ESTADO WALK (Paseo):**
    *   **Condición:** Locomoción de baja intensidad/estable.
    *   **Acción:** El GNSS se activa para obtener un fix cada **30–60 segundos**. La IMU mide actividad en continuo.
    *   **Envío:** Se envían "batches" de datos de actividad (pasos, intensidad) junto con el fix de GNSS.

*   **ESTADO RUN (Carrera):**
    *   **Condición:** Locomoción de alta cadencia/energía.
    *   **Acción:** El GNSS se activa para obtener un fix cada **5–10 segundos**.
    *   **Envío:** Similar a WALK, pero con mayor frecuencia.

*   **ESTADO LIVE (Seguimiento en Vivo):**
    *   **Condición:** Activado por el usuario desde la app.
    *   **Acción:** GNSS y LTE en máxima frecuencia para obtener y enviar un fix cada **2–3 segundos**.

*   **ESTADO LOST (Modo Perdido):**
    *   **Condición:** Activado por el usuario.
    *   **Acción:** No se mantiene una frecuencia fija. Se usan **ráfagas de 2-3 segundos** activadas por eventos de riesgo (aceleración alta, cercanía a borde de geofence) para optimizar la batería durante la búsqueda.

#### 4.1.2. Envíos "Event-Driven" y Datos en "Batch"
Para optimizar el consumo, el dispositivo no envía datos a intervalos fijos (excepto en LIVE). En su lugar:
*   **Acumula métricas de actividad** de la IMU (pasos, cadencia, intensidad, etc.) en la memoria local.
*   Envía estos datos en **"batches"** junto con los fixes de GNSS programados por el scheduler.
*   Puede **disparar envíos adicionales** si detecta eventos de riesgo, como un sprint inesperado o la cercanía al borde de una geofence.

### 4.2. Baterías y Carcasa
*   **Estrategia:** Misma huella (ancho/largo) de 36x58mm (paredes interiores), escalando capacidad solo con el grosor.
*   **Modelos de Batería:**
    *   **Nano (Referencia futura):** 1200mAh (Celda 603450).
    *   **Medium:** ~2750 mAh (Celda 123450).
    *   **Large:** ~4000 mAh (Pack 1S2P, típicamente basado en celda 103450).
*   **Carcasa:** PC/ABS con resistencia IK10. El módulo de batería se integra con el módulo de chip mediante un rail tipo cola de milano y sellado con O-Ring.

### 4.3. Sistema de Iluminación (v4)
*Consolidado de `ARES_HW_V4...` y `Sistema_Luces_ARES.md`*

#### 4.3.1. Arquitectura y Hardware
*   **Diseño:** 2 zonas LED en forma de "L" en esquinas opuestas del dispositivo.
*   **Hardware:** 12 LEDs SMD 1206 de alta intensidad en total (6 por "L": 2 Rojos, 2 Verdes, 2 Azules).
*   **Óptica:** La luz se emite por un chaflán a 45° a través de un difusor de policarbonato mate para crear un efecto "neón" visible a >50m.
*   **Alimentación:** **Directa desde VBAT (3.0–4.2V), SIN booster de 5V.** Cada LED tiene su propia resistencia limitadora.
*   **Control:** 3 canales PWM (R, G, B) del ESP32-S3 controlan 3 MOSFETs N-Channel (low-side) para la mezcla de colores.

#### 4.3.2. Guía de Implementación y Consideraciones
*   **Muro de Seguridad al 15%:** Por debajo de 3.5V (aprox. 15% de batería), la función de encendido manual de luces se bloquea para preservar energía. Solo se permiten destellos informativos de estado (ej. batería baja).
*   **"Ghosting" (Encendido Fantasma):** Para evitar que los LEDs parpadeen durante el arranque, se deben incluir **resistencias de 100kΩ (Pull-down)** en la puerta (gate) de cada MOSFET.
*   **Frecuencia del PWM:** Se recomienda una frecuencia de **1kHz a 4kHz** para evitar parpadeos visibles y posibles interferencias.
*   **Balance de Blancos y Calibración:** Debido a la diferente intensidad de cada color de LED, es necesario aplicar un factor de corrección en el firmware para lograr un color blanco puro y colores consistentes.
    *   `float r_calib = red * 0.60;`
    *   `float g_calib = green * 0.90;`
    *   `float b_calib = blue * 1.0;`
*   **Compensación por Voltaje:** Se debe usar una tabla de calibración (LUT) en el firmware para ajustar el ciclo de trabajo (duty cycle) de R/G/B a medida que baja el voltaje de la batería, asegurando que el color percibido no cambie.

### 4.4. Arquitectura de Energía y Carga
*   **Voltajes:** El sistema opera con una LiPo 1S (3.0V a 4.2V). El módulo de chip regula este voltaje a 3.3V y 1.8V según sea necesario.
*   **Módulo Batería:** Contiene el IC de carga (BQ24040), el circuito de protección (BMS), un sensor de temperatura NTC, y los contactos para la carga magnética.
*   **Carga Magnética:**
    *   **Prioridad:** Carga externa a través de un conector magnético tipo pogo-pin, IP68 y resistente a la corrosión (chapado en oro).
    *   **Corriente:** Soporta ≥2A a 5V.
    *   **Candidatos:** HYTEPRO para prototipos, TE Connectivity para producción.
*   **Conexión Inter-Módulo:** Se usan múltiples pines en paralelo para VBAT y GND (mínimo 2+2, recomendado 4+4) para manejar los picos de corriente del módem LTE sin caídas de tensión.

---
## 5. Análisis de Rendimiento y Optimización

*Extraído de `optimicacion piezas.txt` y actualizado a v4.0*

### 5.1. Análisis de Autonomía (v4.0)
*   **Consumo Diario Estimado:** ~140 mAh (estimación de diseño, aún no validada en banco/campo). Este cálculo se basa en la nueva estrategia de ahorro v4.0, con un uso mixto de 3h de actividad (donde el GNSS se usa de forma intermitente), 12h en valla virtual y 8h de reposo (donde el consumo es mínimo). Ver desglose por fase de actividad (REST/WALK/JOG/RUN/LIVE/LOST) en el modelo de consumo batería+datos del documento de negocio/red.
*   **Duración Estimada por Batería (modelos en alcance de esta especificación: Medium y Large):**
| **Modelo** | **Capacidad** | **Duración Estimada (Días)** |
|------------|---------------|------------------------------|
| **Medium** | **~2750mAh** | **~20 días** |
| **Large** | **~4000mAh** | **~28.5 días** |

*Nota de reconciliación: la fila "Nano (1200mAh, ~8.5 días)" se retira de esta tabla porque el modelo Nano está explícitamente fuera de alcance en esta versión (ver §3.1 "Alcance: enfoque en Medium y Large" en `01_PRODUCTO_Y_NEGOCIO.md`) — mantenerlo aquí como si tuviera cifras de autonomía ya cerradas era una contradicción interna. Si Nano se retoma en una fase futura, su autonomía debe recalcularse con el BOM/batería final de esa fase, no reutilizar esta cifra de referencia.

### 5.1.1. Nota sobre sensórica biométrica (frecuencia cardíaca/pulso)
Se evaluó añadir un sensor óptico dedicado (PPG, tipo MAX30102/MAX86141) para medición directa de pulso, ante la confirmación de que ningún competidor analizado ofrece esto bien (Tractive lo estima algorítmicamente vía IMU, Invoxia usa sensor dedicado). **Decisión: no se añade ningún sensor nuevo a la BOM por ahora** — el contacto óptico a través del pelaje es un reto de diseño industrial no trivial (sonda/paleta con mecanismo de presión, geometría de separación de pelo) y el usuario ha decidido que no es prioritario en esta fase. En su lugar, se implementa una **estimación de esfuerzo/frecuencia respiratoria vía el BMI270 ya existente** (sin cambio de BOM) — ver `docs/specs/v4_final/SPEC_04_INTELLIGENCE_HEALTH.md` §1.4. El sensor PPG dedicado queda documentado como opción descartada-por-ahora en el Risk Register (`RR-004`), no eliminada del radar de producto.

### 5.2. Justificación de Elección de Componentes
*   **Placa Principal (LilyGo T-SIM7000G S3):** Gana por su alta integración (MCU+GPS+Módem), que simplifica el diseño del PCB y acelera la producción.
*   **Sensor IMU (Bosch BMI270):** Pieza central de la arquitectura v4.0. Gana por sus funciones de IA integradas (contador de pasos, detección de movimiento), que son la base para la lógica de ahorro de energía, el sistema anti-fraude y la medición fiable de actividad.
*   **Antena (Ignion A101 + LNA):** La adición de un Amplificador de Bajo Ruido (LNA) es clave para lograr la precisión de <1m requerida, permitiendo fixes de GNSS rápidos y fiables que "anclan" los datos del IMU.
*   **Cargador (Magnético + BQ24040 TI):** Gana por ofrecer la mejor experiencia de usuario (comodidad) y la máxima impermeabilización (IP68) al eliminar puertos USB externos.
