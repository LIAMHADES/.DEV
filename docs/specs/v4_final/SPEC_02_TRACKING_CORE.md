# SPEC_02: Tracking Core, Modos y Conectividad (ARES v4.0)

**Objetivo**: Definir cómo el dispositivo decide cuándo y cómo enviar ubicaciones, garantizando "Trazabilidad Ininterrumpida" (Store & Forward) y eficiencia energética.

## 1. Modos de Funcionamiento (IMU-Driven State Machine)

El dispositivo utiliza la **IMU (Locomoción)** como sensor primario para detectar el estado del perro. El GNSS se activa para anclar la posición y calibrar la zancada.

### 1.1. Estados Locomoción (Fijados por IMU)

1.  **REST (Reposo)**
    - _Detección_: Basado puramente en IMU (sin pasos/cadencia).
    - _GNSS_: Casi siempre OFF (ahorro máximo).
    - _Heartbeat_: Cada 10–30 min (Batería/Estado/Calidad).
2.  **WALK (Paseo/Locomoción Baja)**
    - _Detección_: Cadencia estable detectada por IMU.
    - _Lógica GNSS_: Fix cada 30–60s para anclar ruta.
    - _Telemetría_: Envío batch de pasos/cadencia acumulados.
3.  **RUN (Alta Energía)**
    - _Detección_: Alta cadencia/energía detectada por IMU.
    - _Lógica GNSS_: Fix cada 5–10s.
    - _Eventos_: Envío inmediato en caso de sprint detectado.
4.  **LIVE / LOST (Modos Críticos)**
    - _LIVE_: GNSS continuo (2s) por petición de App.
    - _LOST_: Ráfagas adaptativas de 2s basadas en riesgo (cercanía a geofence o alta aceleración).

### 1.2. Disparadores por Eventos (Event-Driven)

Aunque esté en un estado de frecuencia baja, el dispositivo envía un paquete inmediato si:

- Cambio brusco de dirección detectado por IMU + Brújula.
- Traspaso de Geofence "Near Boundary".
- Degradación súbita de precisión GNSS.
- Sprint / Impacto detectado por IMU.

## 2. Conectividad y "Store & Forward" (Buffer Offline)

La característica clave para la fiabilidad en montaña/bosque.

### 2.1. Lógica del Buffer

1.  **Circular Buffer**: Almacenar puntos en Flash (SPIFFS/LittleFS) cuando falla el envío.
2.  **Estructura**: `[seq_id (4b), ts (4b), lat (4b), lon (4b), telem (8b)]` (~24 bytes/punto).
3.  **Capacidad**: Mínimo 24 horas de ruta (aprox 10k puntos = ~250KB). Si se llena, se sobrescriben los más antiguos.

### 2.2. Protocolo de Envío y Sincronización

1.  **Secuencia**: Cada punto tiene un `seq_id` incremental.
2.  **Intento de Envío**:
    - Si hay red: Enviar punto actual + Lote de 10-50 puntos del buffer (Backfill).
    - Si falla: Guardar punto actual en buffer. No reintentar inmediatamente (ahorro energía). Esperar siguiente ciclo o ventana de conexión.
3.  **ACK**: El servidor responde con `last_seq_id_received`. El dispositivo borra del buffer todo `seq_id <= ACK`.

### 2.3. UX en App

- Estado "Sin Señal": Mostrar "Grabando ruta en memoria...".
- Recuperación: "Subiendo ruta: 45 puntos restantes..." (barra de progreso). _Genera confianza extrema._

## 3. Geofence Inteligente ("Guardia")

El dispositivo (o el backend si es complejo) evalúa la distancia al polígono seguro.

- **Zona Segura (Centro)**: Frecuencia relajada.
- **Zona de Guardia (Borde)**: Al acercarse al perímetro (radio configurable o % del radio), el dispositivo **aumenta la frecuencia de muestreo** (ej. de 1min a 10s).

## 4. Interfaz de Hardware: GNSS ↔ ESP32

Para maximizar la flexibilidad mientras cambiamos componentes, se adopta un enfoque híbrido:

- **Protocolo Universal**: **UART NMEA** (115200 bps). Asegura que cualquier módulo sea "Plug & Play".
- **Modo Alto Rendimiento**: El firmware detectará el modelo de chip y activará el **protocolo Binario** (ej. UBX) si está disponible.
- **Dato Crítico**: Se configurará el GNSS para enviar el valor de **hAcc** (Horizontal Accuracy Estimate), ya sea mediante sentencias binarias o NMEA extendido ($GPGBS), para alimentar el motor de fusión IMU.
