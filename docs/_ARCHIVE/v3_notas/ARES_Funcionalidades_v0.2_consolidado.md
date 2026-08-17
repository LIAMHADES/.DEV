# ARES — Especificación completa de funcionalidades (Tracker + App + Nube)  
**Versión:** v0.1 (consolidada)  
**Última actualización:** 2026-01-11  
**Producto:** Tracker para perros activos (trail/running/bici) + app móvil + backend  

---

## 1) Objetivo del documento
Dejar cerrado **qué hace el sistema**, **cómo lo hace**, **qué componente lo habilita** y **dónde se implementa** (firmware/app/backend), evitando ambigüedades.  
Incluye además contratos mínimos (datos, topics/endpoints, estados) para que hardware, firmware, backend y app avancen alineados.

---

## 2) Stack técnico (lenguajes y tecnologías)
- **Firmware (dispositivo):** **ESP32-S3 LilyGo T-SIM7000G** en **C/C++** (PlatformIO) + comandos **AT** al módem **SIM7000G**.  
- **Transporte:** **MQTT** (principal) + **HTTP** (fallback) + TLS en producción.  
- **Broker MQTT:** EMQX (o equivalente).  
- **Backend:** **Python/FastAPI** + **PostgreSQL + PostGIS** + workers (colas) + (opcional) **Node-RED** para orquestación de alertas.  
- **App móvil:** **Flutter (Dart)** + BLE + Maps + cliente MQTT/WebSocket.

---

## 3) Arquitectura del sistema (visión rápida)
**Dispositivo → Nube → App**
1. Dispositivo calcula estado (IMU), decide tasa GNSS, y envía telemetría por LTE-M/NB-IoT.  
2. Backend ingiere, valida, persiste (PostGIS), recalcula “verdades oficiales” (km válidos, anti-fraude), y genera alertas.  
3. App consume tiempo real (stream) + histórico, gestiona geofences y modo perdido, y muestra métricas/alertas/social.

**Canales:**
- **LTE-M/NB-IoT**: tracking global + telemetría.  
- **BLE**: búsqueda cercana + configuración local.  
- **WiFi**: configuración/OTA y “backup urbano” (WiFi sniffing).

---

# BLOQUE 1 — Funcionalidades dependientes del hardware (dispositivo)

## 4) Posicionamiento exacto (Prioridad #1)
### 4.1 Qué hace
- **Tracking real del perro** (no del móvil): posición y estado casi en tiempo real.
- **Precisión objetivo:** <2 m en condiciones buenas (con calidad GNSS alta).  
- **Cobertura global:** mediante LTE-M/NB-IoT + SIM IoT.  
- **Anti-multipath (urbano/bosque/edificios):** no es “mágico”; se implementa con filtros y reglas de calidad de señal.

### 4.2 Componentes
- **LilyGo T-SIM7000G (ESP32-S3 + SIM7000G)** (CPU + GNSS + LTE-M/NB-IoT)
- **Antena GNSS/LTE** (p.ej. IGNION A101 u otra equivalente)

### 4.3 Reglas de calidad GNSS (anti-saltos)
- Rechazar/etiquetar puntos si:
  - `accuracy` > umbral (N)  
  - `satellites` < umbral (M)  
  - saltos imposibles (distancia/tiempo incompatibles con la IMU y velocidad)  
- Suavizado opcional (media móvil / filtro) **solo para UI**, manteniendo el “raw” para auditoría.

---

## 5) Modos de tasa GNSS (contrato explícito con app)
> Esto debe quedar como “tabla de verdad” para que la app pueda mostrar **autonomía estimada** consistente.

### 5.1 Tabla de modos GNSS
| Modo | Condición | Tasa GNSS | Nota |
|---|---|---:|---|
| **RUN** | `activity_mode=RUN` y `activity_score > X` | **2s** | Máxima precisión/consumo |
| **JOG** | `activity_mode=JOG` | **5s** | Equilibrio |
| **WALK** | `activity_mode=WALK` | **10s** | Uso general |
| **GEOFENCE-NEAR** | `<15%` distancia al límite | **2s** | Sobrescribe por seguridad |
| **GEOFENCE-MID** | `15–30%` al límite | **10s** | Sobrescribe |
| **GEOFENCE-FAR** | `>30%` al límite | **30s** | Ahorro agresivo |
| **REST** | inmóvil + sin evento IMU | **OFF** | Solo IMU |
| **LOST_MODE** | activado desde app/backend | **2s continuo** | por X min o hasta cancelar |

### 5.2 Consumo “de catálogo”
- Cada modo debe tener un **consumo medio medido** (mA promedio) en prototipo.  
- La app usa la tabla para mostrar:
  - **autonomía estimada**,  
  - **impacto** de activar LOST_MODE,  
  - **modo actual** y su coste.

---

## 6) Detección de movimiento inteligente (IMU) + activity_score
### 6.1 Qué hace
- Diferencia **reposo vs movimiento** sin tener GNSS siempre encendido.
- Clasifica **caminar/trote/correr** y detecta patrones de **vehículo**.
- Alimenta:
  - control de tasa GNSS,  
  - cálculo de actividad,  
  - anti-fraude.

### 6.2 Campos formales (obligatorio)
- `activity_mode` (enum): `REST`, `WALK`, `JOG`, `RUN`, `VEHICLE`  
- `activity_score` (0–100): intensidad + duración (definición exacta en backend; el firmware puede emitir un preliminar)

### 6.3 Reglas base (ejemplo orientativo)
- IMU a baja frecuencia en reposo + **wake-on-motion**.  
- Ventana de validación (ej. 10s):
  - si micro-movimiento (rascado) → volver a sleep  
  - si cadencia estable → WALK/JOG/RUN  
  - si velocidad alta sostenida + aceleración “plana” → VEHICLE

---

## 7) Anti-fraude (mínimo viable)
### 7.1 Qué hace
Evita que los km/rewards se inflen por coche o por puntos GNSS malos.

### 7.2 Señales (device)
- `activity_mode=VEHICLE`  
- `speed` (GNSS) + consistencia con IMU  
- saltos imposibles (distancia/tiempo)

### 7.3 Fuente de verdad
- La **validación oficial** para rankings/rewards es del **backend** (ver BLOQUE 2).

---

## 8) Geofence adaptativa (valla inteligente)
### 8.1 Qué hace
- Permite definir zonas seguras (casa, parque, finca) y alerta al salir/entrar.
- Ajusta la tasa GNSS según proximidad (tabla anterior).

### 8.2 Implementación
- Geofence se define en backend/app; el dispositivo recibe:
  - centro + radio (círculo) o polígono (fase 2)  
- El dispositivo puede aplicar “pre-check” local para subir tasa al acercarse.

---

## 9) Modo perdido (LOST_MODE) — formalizado en firmware
### 9.1 Qué hace
- Forzar tracking extremo durante una ventana corta para recuperar al perro:
  - **GNSS 2s continuo**  
  - LTE sin duty-cycle (hasta timeout)

### 9.2 Trigger y salida
- Trigger: comando remoto (MQTT/HTTP → backend → dispositivo)  
- Salida:
  - cancelación manual  
  - timeout X minutos  
  - batería baja crítica (fallback a modo seguro)

### 9.3 Feedback
- LED patrón específico (ej. blanco intermitente).

---

## 10) Política GNSS degradado (sin cielo) + marcado explícito
### 10.1 Qué hace
En urbano denso/interior, GNSS puede ser inusable. El sistema entra en modo degradado y **marca** la fuente.

### 10.2 Campo obligatorio
- `position_source`: `GNSS`, `CELL`, `WIFI`, `MIXED`

### 10.3 Regla de entrada
- Si `gps.accuracy > N` o `satellites < M` durante `T` segundos → degradar.

### 10.4 Qué se espera
- **CELL (Cell ID/LBS):** precisión baja (aprox)  
- **WIFI sniffing:** precisión variable (depende densidad de APs)  
- App muestra **“posición aproximada”** y esos puntos **no** cuentan para rankings/calorías finas.

---

## 11) Gestión de energía optimizada (autonomía real)
### 11.1 Objetivo
- **5–7 días** en uso intensivo (según batería)  
- Deep sleep agresivo + duty-cycle inteligente  
- Protección térmica

### 11.2 Estados mínimos de firmware
- `SLEEP` (IMU vigilando)  
- `VALIDATE_MOVE`  
- `TRACKING`  
- `CHARGING`  
- `LOST_MODE` (excepción)

### 11.3 Batería modular
- Packs 2000/3000/4500 mAh (si se mantiene modularidad).
- Telemetría energía:
  - `battery_mv`, `battery_pct`, `temperature`

### 11.4 Carga (decisión de versión: conflicto a resolver)
**Opción A — USB-C (MCP73831 u otro cargador lineal):**
- Ventaja: simple, barato.  
- Riesgo: **IP68 real** más difícil con puerto.

**Opción B — magnética/pogo (sellado mejor):**
- Ventaja: mejor para IP68.  
- Requiere diseño de contactos + cargador adecuado.

**Opción C — inalámbrica (Qi u otra):**
- Ventaja: sin agujeros.  
- Coste/eficiencia/espacio: a validar.

> Mientras no se decida, el documento marca carga como “Versionado”.

### 11.5 Protección térmica (NTC)
- Si `temperature > 45°C` (umbral ejemplo) → pausar carga / limitar consumo.

---

## 12) Comunicación multi-nivel
### 12.1 LTE-M/NB-IoT (primario)
- Publica telemetría por MQTT (preferente) o HTTP.
- Soporta **store & forward**: buffer local y envío batch al recuperar señal.

### 12.2 BLE (búsqueda cercana + config)
- “Find nearby” por RSSI (caliente/frío).
- Configuración inicial (onboarding) sin nube si hace falta.
- Nombre BLE/tag: p.ej. `Roco_Finder_123` (configurable).

### 12.3 WiFi (config/OTA + backup urbano)
- WiFi AP temporal para setup: `Roco_Setup_123`
- OTA preferente por WiFi en casa.
- WiFi sniffing para modo degradado (envía lista de BSSID/SSID).

---

## 13) Feedback visual/auditivo
### 13.1 LED RGB (WS2812B)
- Estados: batería, GNSS fix, conexión LTE, LOST_MODE, error.



---

## 14) Monitorización ambiental
- `temperature` para índice de calor / seguridad y para protección térmica.  
- Resistencia:
  - objetivo **IP68** (agua/polvo)  
  - resistencia golpes ~2 m (a validar con pruebas)

---

## 15) Robustez y fiabilidad (para que no “muera” en campo)
- Watchdog y auto-recover de cuelgues.
- Reconexión con backoff (evitar tormentas).
- Buffer circular y deduplicación por `seq_id`.
- OTA segura (ideal A/B con rollback).
- Diagnóstico mínimo:
  - `fw_version`, `last_reset_reason`, `uptime_s`
  - logs resumidos (contador de fallos GNSS/LTE)

---

## 16) Seguridad mínima (sin sobrediseñar)
- Identidad por `device_id` + autenticación.
- TLS para MQTT/HTTP (prod).
- Comandos firmados/validados (al menos token por dispositivo).
- OTA con firma de firmware (fase 2 si no entra en v1).

---

## 17) Componentes hardware definidos (BOM funcional)
> Integración directa de la lista que ya tenías + los matices de versionado.

### 17.1 Cerebro + comunicaciones
- **LilyGo T-SIM7000G (ESP32-S3 + SIM7000G)**: CPU + BLE + WiFi + GNSS + LTE CAT-M1/NB-IoT + 8MB PSRAM  
- **Antena IGNION A101** (o equivalente): GNSS/LTE/WiFi según diseño final

### 17.2 Sensores
- **MPU6050**: IMU 6 ejes  
- **NTC 10kΩ**: temperatura/protección

### 17.3 Energía + carga
- **LiPo 3.7V** (2000/3000/4500 mAh) + conector **JST-PH 2.0** (si modular)  
- **MCP73831** (si versión USB-C) u otro cargador según versión final  
- **WS2812B**: LED RGB

### 17.4 Carcasa + PCB
- **PCB 4 capas**  
- **Carcasa PC/ABS** (objetivo IP68) + coating/potting recomendado

---

# BLOQUE 2 — Funcionalidades de App + Nube

## 18) Separación de responsabilidades (App vs Backend)
### App (Flutter)
- UI mapa real-time + detalle del tracker
- Onboarding y configuración (BLE/WiFi)
- Geofence UI + preferencias de alertas
- “Find nearby” (RSSI) + guía visual/háptica
- Cálculos aproximados en vivo (km/calorías) para feedback inmediato
- Social/privacidad desde UI

### Backend (FastAPI/PostGIS + servicios)
- Ingesta + validación + persistencia
- Streaming a app (realtime)
- Motor de alertas (geofence, batería, inmovilidad, calor, pérdida de señal)
- Anti-fraude completo y **km válidos oficiales**
- Rewards/cupones + suscripciones/tiers
- IA nutrición/recomendaciones (si aplica)

---

## 19) Onboarding completo (usuario + perro + dispositivo)
Para que salud/recomendaciones funcionen desde el día 1, onboarding pide:
- **raza**
- **edad**
- **sexo**
- **peso**
- **esterilización**
- **nivel de actividad típico**

Se guarda como `dog_profile`.

---

## 20) Multi-perro y multi-usuario (familia)
Modelo mental (obligatorio para evitar caos):
- Un usuario puede tener **N perros**.  
- Un perro puede ser visible por **varios usuarios** (familia/grupo).  
- Un dispositivo se vincula a **1 perro a la vez** (con cambio guiado y logs).  
- Las alertas se configuran por **perro y usuario**.

---

## 21) Privacidad mínima (modo social)
- Ranking por defecto muestra **alias**, no nombre real.  
- Social no expone posición exacta a terceros: solo estadísticas/rutas resumidas.  
- Opción **perfil privado** (no aparece en rankings/grupos públicos).

---

## 22) Tiers (Gratis / Plata / Oro) — tabla de referencia única
> Objetivo: evitar textos contradictorios. Donde falte detalle: **TBD**.

| Bloque | Gratis | Plata | Oro |
|---|---|---|---|
| Tracking | Real-time + histórico 7 días | Histórico 30 días (TBD) | Histórico 1 año |
| Salud | km/calorías aprox | IA completa 1 perro (TBD) + Diet Fuel BASIC | Diet Fuel PRO + métricas avanzadas (TBD) |
| Social | Básico | Grupos/challenges locales + ranking local (TBD) | Ranking nacional + “Strava perro” (TBD) |
| Rewards | Básicos | Cupones 15% (TBD) | Cupones 20% + VIP (TBD) |
| Límites | 1 perro | 1 perro | 2–3 perros |

---

## 23) Matriz de alertas (qué, quién, canal, tier)
| Alerta | Genera | Canal | Tiers |
|---|---|---|---|
| Geofence (sale/entra) | Backend (regla) + Device (tasa) | Push; opcional WhatsApp/email | Gratis+ |
| Batería baja | Device + Backend | Push | Gratis+ |
| Pérdida de señal | Backend | Push; email opcional | Plata+ (TBD) |
| Inmovilidad anómala | Backend | Push urgente | Plata+ (TBD) |
| Calor/índice riesgo | Device (temp) + Backend | Push + banner | Plata+ (TBD) |
| Reward conseguido | Backend | Push + badge | Gratis+ |

---

## 24) Qué se calcula dónde (km y calorías)
- **App:** estimación en vivo (para sensación de inmediatez).  
- **Backend:** recalcula km válidos aplicando anti-fraude completo → rankings, calorías “serias”, rewards.

---

# CONTRATOS — Topics, endpoints y payloads

## 25) MQTT topics (mínimo)
- `devices/{device_id}/telemetry`  (**PUB** dispositivo)  
- `devices/{device_id}/commands`   (**SUB** dispositivo)  
- `users/{user_id}/realtime`       (**PUB** backend → app)

## 26) HTTP API mínima
- `POST /api/v1/ingest`  (punto suelto o batch store&forward)  
- `GET  /api/v1/devices/{id}/history?from=&to=`  
- `POST /api/v1/devices/{id}/lost-mode` (activar/desactivar)  
- `POST /api/v1/rewards/claim`

---

## 27) Payload mínimo de telemetría (JSON v1)
```json
{
  "device_id": "ares-001",
  "seq_id": 123456,
  "ts": "2026-01-11T12:34:56Z",
  "position": {
    "lat": 40.4168,
    "lon": -3.7038,
    "accuracy": 2.1,
    "satellites": 18,
    "speed": 3.2,
    "source": "GNSS",
    "gnss_rate_s": 2
  },
  "state": {
    "status": "MOVING",
    "activity_mode": "RUN",
    "activity_score": 84,
    "gnss_rate_s": 2
  },
  "power": {
    "battery_mv": 3920,
    "battery_pct": 76,
    "temperature_c": 31.4
  },
  "integrity": {
    "fw_version": "0.1.0",
    "uptime_s": 8421,
    "last_reset_reason": "WDT"
  }
}
```

## 28) Comandos mínimos (backend → dispositivo)
- `SET_LOST_MODE` (on/off + timeout)  
- `SET_GEOFENCE` (circular v1)  
- `PING` (healthcheck)  
- `SET_RATE_PROFILE` (opcional)  
- `START_OTA` (fase 2+)

---

# 29) Checklist de requisitos implementables (plantilla)
Tabla recomendada: **ID – Funcionalidad – Bloque – Tier – Owner – Estado**

Ejemplos:
- `FW-001` Emitir `activity_mode` + `activity_score` en telemetría  
- `FW-010` LOST_MODE (2s continuo + timeout)  
- `BE-020` Motor geofence + push  
- `APP-005` Mapa real-time + indicador de precisión/fuente

---

# 30) Decisiones pendientes (para cerrar v1 sin contradicciones)
2. **Carga final**: USB-C vs magnética/pogo vs inalámbrica (impacto IP68).  
3. **Umbrales** oficiales: N/M/T para degradado GNSS; X para activity_score RUN.  
4. **OTA**: entra en v1 o v1.5 (y si será A/B con rollback).  
5. **Tiers**: cristalizar definitivos (sin solape) y sus límites exactos.

---

## 31) “Verdict” (lo que queda 100% definido ya)
- GNSS + LTE-M como columna vertebral de tracking.  
- IMU para wake-on-motion, clasificación, anti-fraude y ahorro de batería.  
- Geofence adaptativa con tasa GNSS ligada a proximidad.  
- LOST_MODE formalizado con comando remoto.  
- Política de degradación GNSS con `position_source` explícito.  
- Contrato mínimo de telemetría con campos clave y `seq_id`.  
- Separación clara app vs backend y “verdad oficial” en backend.

