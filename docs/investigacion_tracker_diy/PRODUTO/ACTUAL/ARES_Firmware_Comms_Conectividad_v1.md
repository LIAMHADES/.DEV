# ARES v4.0 — Documento técnico para generación de firmware (comunicación, latencia, datos, eSIM) y riesgos
**Propósito:** servir como referencia única para implementar el firmware del dispositivo (Módulo A “Cerebro”) y su integración con backend/app. Incluye **cómo se comunica**, **qué necesita para funcionar**, **presupuesto de datos**, **latencia esperable**, y **fallos típicos** + mitigaciones.

---

## 1) Fuente de verdad y compatibilidad entre documentos
**Fuente de verdad (prioridad alta):**
1) `ARES_v4.0_Estrategia_IMU-GNSS.md` (Estrategia maestra de firmware y producto)
2) `02_ESPECIFICACION_TECNICA.md` (hardware v4.0 + decisiones finales)
3) `04_GUIA_FIRMWARE.md` (lógica de firmware v4.0)
4) `ARES_APP_Spec_v0.2_consolidado.md` (contratos app/backend, topics, payloads)

**Nota importante de coherencia:**
- Las menciones antiguas a **WS2812B** y **MPU6050** quedan **obsoletas** en v4.0. La BOM final define **LEDs analógicos 1206 + MOSFETs** y **IMU Bosch BMI270**.
- Las tasas de refresco fijas (ej. RUN=3s) quedan obsoletas y son reemplazadas por el scheduler dinámico definido en la estrategia v4.0.

---

## 2) Arquitectura del dispositivo (lo que existe físicamente y para qué sirve)
### 2.1 Módulos
**Módulo A — CEREBRO (36×58mm huella / PCB chip 37×28):**
- **LilyGo T-SIM7000G S3 (ESP32-S3 + SIM7000G + GNSS + LTE-M/NB-IoT + WiFi + BLE)**: CPU, conectividad y GNSS.
- **Bosch BMI270**: Sensor primario de actividad (locomoción, pasos, cadencia, intensidad) y disparador de estados.
- **Antena Ignion A101 + LNA**: mejora GNSS/LTE (según diseño final de RF).
- **eSIM 1NCE soldada**: conectividad IoT.
- **12× LEDs 1206 (2R+2G+2B por “L”)** + **3× MOSFET (AO3400A)**: feedback visual (PWM RGB analógico) sin booster 5V.
- **NTC 10k**: protección térmica.
- **PCB 4 capas**: estabilidad RF/EMI.

**Módulo B — POWER PACK:**
- LiPo 1S (3.0–4.2V), packs modulares.
- Gestión de carga (BQ24040) + carga magnética IP68.
- Múltiples pines en paralelo para **VBAT/GND** para aguantar picos del módem.

### 2.2 Qué necesita para funcionar (dependencias “hard”)
- **VBAT estable**: diseño de pistas/pines para picos LTE (si hay caída → resets/latencia).  
- **Antena y RF**: layout y material de carcasa no deben degradar GNSS (especial cuidado con grosor/material cerca de antena).
- **Temperatura**: si NTC >45°C (umbral ejemplo), limitar carga/consumo.
- **Identidad única**: `device_id` (firmware), y mapeo a `dog_id`/`user_id` en backend.

---

## 3) Flujo de comunicación: dispositivo ⇄ servidores ⇄ teléfono
### 3.1 Principio
- El **dispositivo es la fuente de telemetría**.
- La app **no es puente obligatorio** (salvo BLE y modo "Phone-Assist").

### 3.2 Canales
1) **Dispositivo → Backend (primario)**
- **MQTT** (preferente) hacia broker (EMQX).
- **HTTP** (`POST /api/v1/ingest`) como fallback o para batch (store&forward).

2) **Backend → App (tiempo real)**
- MQTT over WebSocket o WebSocket propio, publicado por backend en topic por usuario/perro.

3) **App ↔ Dispositivo (cercanía / setup)**
- **BLE**: pairing, diagnóstico local, “Find Nearby”, “Phone-Assist”.
- **WiFi AP temporal**: setup/OTA preferente en casa (`Roco_Setup_123` / “WiFi conocida”).

### 3.3 Contratos técnicos (topics y endpoints)
**MQTT topics mínimos:**
- `devices/{device_id}/telemetry` (PUB device)
- `devices/{device_id}/commands` (SUB device)
- `users/{user_id}/dogs/{dog_id}/realtime` (PUB backend → app)

**HTTP mínimo:**
- `POST /api/v1/ingest` (punto suelto o batch)
- `POST /api/v1/devices/{id}/lost-mode` (on/off + timeout)

---

## 4) Payload de telemetría y control (lo que debe implementar el firmware)
### 4.1 Telemetría v4.0 (device → backend)
El payload se envía en "batches". Cada envío incluye el último fix de GNSS y un resumen de la actividad desde el último envío.

**Campos obligatorios:**
- `device_id`
- `seq_id` (monótono para deduplicación)
- `ts` (UTC del momento del envío)
- **`gnss_fix`** (Objeto, puede ser nulo si no hay fix disponible):
  - `ts`: (UTC del fix)
  - `lat`, `lon`, `acc` (accuracy), `sats` (satellites), `spd` (speed)
- **`activity_batch`** (Array de objetos, uno por cada minuto de actividad):
  - `ts`: (UTC del inicio del minuto)
  - `steps`: (conteo de pasos en ese minuto)
  - `cadence_avg`, `cadence_max`: (pasos/min)
  - `intensity_avg`: (score 0-100)
  - `time_in_rest_s`, `time_in_walk_s`, `time_in_run_s`: (segundos en cada estado)
  - `events`: (Array de strings, ej: ["sprint_start", "hard_turn"])
- **`power`**: 
  - `bat_mv` (milivoltios), `bat_pct` (%), `temp_c` (temperatura)
- **`comms`**:
  - `rssi`, `net_type` (LTE-M/NB-IoT/2G)
- **`integrity`**: `fw_version`

### 4.2 Comandos (backend → device)
**LOST_MODE** (mínimo):
- `enabled` (true/false)
- `timeout_s` (recomendado)
- `reason`

### 4.3 Robustez de envío
- Implementar **store & forward**:
  - Buffer circular local (flash/PSRAM) para guardar los `activity_batch` y `gnss_fix`.
  - Cuando no hay señal, guardar y enviar en un batch más grande al recuperar conexión.
- Deduplicación:
  - `seq_id` + `device_id` permite deduplicar en backend.

---

## 5) Máquina de Estados v4.0 (IMU-driven)

Esta sección reemplaza la lógica antigua basada en velocidad. El firmware opera con una máquina de estados gobernada por la actividad detectada en la IMU (BMI270).

*   **ESTADO REST (Reposo):**
    *   **Condición:** Sin locomoción detectada por la IMU.
    *   **Acción:** GNSS y Módem LTE en modo de bajo consumo o apagados.
    *   **Envío:** Heartbeat de estado/batería cada **10–30 minutos**.

*   **ESTADO WALK (Paseo):**
    *   **Condición:** Locomoción de baja intensidad/estable.
    *   **Acción:** El GNSS se activa para obtener un fix cada **30–60 segundos**.
    *   **Envío:** "Batch" de actividad acumulada + fix GNSS.

*   **ESTADO RUN (Carrera):**
    *   **Condición:** Locomoción de alta cadencia/energía.
    *   **Acción:** El GNSS se activa para obtener un fix cada **5–10 segundos**.
    *   **Envío:** "Batch" de actividad acumulada + fix GNSS.

*   **ESTADO LIVE (Seguimiento en Vivo):**
    *   **Condición:** Activado por el usuario desde la app.
    *   **Acción:** GNSS y LTE en máxima frecuencia para obtener y enviar un fix cada **2–3 segundos**.
    *   **Envío:** Payload mínimo (solo GNSS) para minimizar latencia.

*   **ESTADO LOST (Modo Perdido):**
    *   **Condición:** Activado por el usuario.
    *   **Acción:** No se usa una frecuencia fija. Se emplean **ráfagas de 2-3 segundos** activadas por eventos de riesgo (aceleración, cercanía a geofence) para optimizar la batería.

Además:
- **Geofence adaptativa**: cerca del borde, subir frecuencia de fix/envío.
- **WiFi conocida**: apagar GNSS/LTE por completo.
- **Anti-fraude**: Si velocidad GNSS > 25 km/h y BMI270 estacionario → clasificar como `VEHICLE` y no contar actividad.

---

## 6) Latencia y Modo LIVE: qué puede fallar y cómo evitarlo
### 6.1 Lo que define la latencia real (orden de impacto)
1) **Tecnología disponible** (LTE-M vs NB-IoT) y cobertura local.
2) **Perfil de ahorro del módem** (PSM/eDRX). Si está “durmiendo”, la latencia sube a segundos.
3) Reconexiones (RRC resume), DNS, TLS handshake, MQTT session.
4) Backend (ingesta, broker, colas) y app (render throttling).

### 6.2 Reglas para que el Modo LIVE (2-3s) sea viable
- El modo debe forzar un **perfil de radio "awake"**:
  - PSM desactivado o mínimo.
  - eDRX mínimo o desactivado.
  - Mantener sesión MQTT viva (keepalive razonable).
- Si la señal es mala (ej. cae a NB-IoT), el firmware debe degradar automáticamente la frecuencia a 5–10s y la app debe mostrar la "edad del último punto".

### 6.3 Decisión de tasas de refresco (v4.0)
La antigua incongruencia de 2s vs 3s queda resuelta. Las tasas ahora dependen del estado:
- `RUN` normal: 5-10s.
- `LIVE` o `LOST` (en ráfaga): 2-3s.
- Todos los modos de alta frecuencia deben tener un **timeout** estricto (ej. 10–15 min) para preservar batería y datos.

---

## 7) Presupuesto de datos (objetivo: ~0.25 GB/mes por perro) y cómo controlarlo
### 7.1 Modelo de cálculo v4.0
El nuevo modelo de "batching" cambia el cálculo. El objetivo es reducir el **número de transmisiones LTE**, que es lo que más consume energía y datos por el overhead de la conexión.

- **Payload:** El tamaño del payload de telemetría (`activity_batch` + `gnss_fix`) puede ser mayor que un simple punto GPS.
- **Frecuencia:** Pero la frecuencia de envío es mucho menor en los modos `WALK` y `REST`.
- **Resultado:** Se reduce el consumo total de datos y batería al minimizar las costosas conexiones a la red.

### 7.2 Palancas directas para ahorrar datos
1) **Batching agresivo:** Agrupar la mayor cantidad posible de datos de actividad en un solo envío.
2) **Modo LIVE con timeout:** Limitar estrictamente el tiempo que un usuario puede estar en modo de 2-3s.
3) **Serialización compacta** (CBOR/Protobuf) en vez de JSON si el tamaño del payload se vuelve un problema.
4) **Throttling en app**: no renderizar cada punto si llega muy rápido.
5) **Keepalive y QoS correctos**: evitar reconexión por punto.

---

## 8) Estrategia SIM/eSIM y Conectividad (v1.0)
(Esta sección permanece sin cambios)

### 8.1 Fases de implementación de SIM
...
### 8.2 Proveedor: 1NCE
...
### 8.3 Riesgos Típicos de Conectividad y Mitigaciones en Firmware
...

---

## 9) Sistema de iluminación (relevante para firmware y riesgos)
(Esta sección permanece sin cambios)
...

---

## 10) Lista de fallos críticos (y mitigaciones) — checklist para firmware
(Esta sección permanece sin cambios, ya que los riesgos son consistentes con la nueva arquitectura)
...

---

## 11) Requisitos mínimos para “Ready for Field Test” (sin excusas)
**Firmware:**
- **Scheduler v4.0** implementado (REST/WALK/RUN/LIVE/LOST).
- **Batching de actividad** y envío con GNSS.
- MQTT estable + fallback HTTP ingest.
- Store&forward + dedup.
- Medición batería/temperatura + protecciones.
- LED patterns (estado + find) + LUT.
- **OTA preferente por WiFi conocida, fallback a celular solo si no hay WiFi disponible tras N días sin actualizar** (ver `ARES_Analisis_Red_y_Consumo_v1.md` §2 — evita que las actualizaciones de firmware compitan con el presupuesto de datos de telemetría).

**Backend:**
- Ingest de payloads v4.0 (con `activity_batch`).
- Broker EMQX + ACL por device/user.
- Endpoint de lost-mode y publicación de comandos.

**App:**
- Realtime con throttling.
- UI con “edad del punto”, modo perdido, estado de tracker.

---

## 12) Decisiones pendientes (para cerrar antes de “producción”)
1) **Umbrales exactos de la IMU** para transicionar entre REST/WALK/RUN.
2) **Tamaño y medio del buffer offline** (flash vs PSRAM vs externo).
3) **Política de PSM/eDRX** por estado (tabla de configuración).
4) **Política de cuotas (tiers)** y límites de Live/Lost para asegurar ~250MB/mes.
5) **Modelo de personalización** por raza/tamaño para la calibración de la IMU.
