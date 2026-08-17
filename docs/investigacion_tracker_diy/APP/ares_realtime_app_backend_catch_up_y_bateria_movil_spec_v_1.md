# ARES — Protocolo realtime app↔backend + Catch-up + Batería móvil (Spec v1)

## Objetivo
Que al abrir la app/mapa el usuario vea **dónde está el perro “ya”** y que el recorrido se cargue **sin fallos ni duplicados**, manteniendo **batería móvil** bajo control.

---

## 1) Decisión de arquitectura
### 1.1 Canales
- **HTTP (REST)**: autenticación, planes/códigos, configuración, **catch-up** (histórico/track), estado actual, assets.
- **MQTT over WebSocket**: **stream realtime** (solo cuando el mapa está en primer plano).
- **Push (FCM/APNS)**: alertas críticas en background (escape/geofence, batería baja, offline, caregiver activa Modo Perdido, etc.).

### 1.2 Regla de batería móvil (obligatoria)
- **MQTT solo con pantalla activa** (mapa abierto / pantalla activa en foreground).
- Al pasar a background: **cortar MQTT**.
- En background: solo **push** + **refresh puntual** cuando el usuario abre la notificación o vuelve a la app.

---

## 2) Identidades y permisos (topics + ACL)
### 2.1 Identidades
- Se manejan **ambos IDs**:
  - `device_id` (tracker)
  - `dog_id` (perro)

### 2.2 Reglas de acceso al live (stream)
- **Owner**: siempre puede suscribirse a live.
- **Caregiver**: puede suscribirse a live **solo dentro de su ventana temporal activa**.
- Fuera de ventana: denegar subscripción live (ACL).

### 2.3 Topics recomendados
> Nota: el backend puede mapear dog_id↔device_id internamente.

- Live ubicación:
  - `dog/{dog_id}/location/live`
- Estado dispositivo:
  - `dog/{dog_id}/device/state`
- Alertas/eventos:
  - `dog/{dog_id}/alerts`
- (Opcional debug/ops interno):
  - `device/{device_id}/telemetry`

### 2.4 Autenticación
- App obtiene token (JWT/OAuth) por HTTP.
- MQTT over WS se autentica con ese token.
- Broker aplica ACL por roles (Owner/Caregiver) y validez temporal.

---

## 3) Modelo de datos en servidor (para “siempre actualizado”)
### 3.1 Dos capas de track (obligatorio)
1) **RAW Track (inmutable)**
- Guarda **todos** los puntos recibidos (sin perder detalle), con idempotencia.

2) **VIEW Track (precalculado / optimizado)**
- Versión condensada para pintar rápido el mapa.
- Se genera automáticamente al ingerir puntos (o por job rápido) para que el móvil no espere cálculos.

### 3.2 Idempotencia y deduplicación (100% server-side)
Cada punto debe incluir:
- `device_id`
- `boot_id` (UUID por arranque del dispositivo)
- `seq_id` (contador incremental por boot)
- `ts` (timestamp)
- `lat`, `lon`
- `accuracy_m` (si existe)
- `source` (GNSS/WiFi/BLE/Cell/…) si aplica

**Clave de idempotencia:** `(device_id, boot_id, seq_id)`
- Si llega repetido: se ignora.
- Orden por `ts` y/o `seq_id`.

### 3.3 Condensación (VIEW Track)
- El servidor decide cómo “empaquetar” para el móvil:
  - simplificación geométrica (tipo Douglas–Peucker) o
  - muestreo adaptativo por ventanas (más denso en giros, menos en rectas).
- Objetivo: mantener fidelidad visual y precisión sin saturar red/UI.

---

## 4) UX: al abrir mapa tras horas (Catch-up)
### 4.1 Requisito de latencia
- **1–2 s** para mostrar:
  - **posición actual** (o la más reciente disponible)
  - estado actual (online/offline/sincronizando, batería, modo)
- Carga completa del recorrido orientativo:
  - progresiva, con objetivo **<= 5 s** para “ruta útil”, y luego refinado si se necesita.

### 4.2 Estrategia “Fast First, Refine Later” (obligatoria)
Al abrir el mapa:

**Fase 0 (inmediata, prioridad máxima)**
- Pedir por HTTP un paquete mínimo (“NOW”):
  - `last_fix` (último punto)
  - últimos **10–15 s** de puntos (si existen)
  - `device_state` (batería, señal, modo, último contacto)
- Render:
  - marcador “posición actual”
  - mini-traza reciente (si llega)

**Fase 1 (catch-up orientativo, rápido)**
- Pedir por HTTP “VIEW Track” desde `last_seen_ts` (la última vez que el usuario abrió el mapa).
- Render:
  - ruta “orientativa” completa desde última sesión (sin bloquear UI)

**Fase 2 (refinado por tandas)**
- Si el usuario se queda mirando:
  - el servidor envía lotes adicionales (más densidad) por HTTP (no por MQTT) para segmentos donde haga falta más precisión.
- Regla:
  - el refinado no puede impedir que el usuario vea ya la posición actual.

**Fase 3 (realtime)**
- Abrir **MQTT over WS** y suscribirse al live.
- Deduplicar cualquier solape entre:
  - puntos del catch-up (HTTP)
  - primeros puntos del stream (MQTT)

### 4.3 “Desde la última vez” (tu opción C)
- La app guarda `last_seen_ts` por perro (cuando el usuario salió del mapa).
- Catch-up se solicita con `since=last_seen_ts`.
- Si `last_seen_ts` no existe (primera vez), usar ventana por defecto (ej. 2h o 24h; se define en producto).

---

## 5) Límite de puntos (qué significa y por qué)
> Esto no limita lo que guarda la nube; limita lo que **se envía y pinta** en el móvil por rendimiento.

### 5.1 Reglas de payload
- “NOW packet” (Fase 0): máximo ~20–60 puntos (10–15 s según frecuencia).
- “VIEW Track” (Fase 1): entregar una ruta simplificada con un máximo recomendado:
  - **500–1000 puntos** por respuesta (ajustable por dispositivo/OS).
- “Refine batches” (Fase 2): lotes pequeños por tramo (ej. 100–300 puntos) bajo demanda.

### 5.2 Principio
- Guardar RAW completo siempre.
- Enviar VIEW para pintar rápido.
- Refinar solo si el usuario lo necesita.

---

## 6) Estado visual mínimo (banner / indicadores)
### 6.1 En uso normal (no molestar)
- Mostrar discreto:
  - “Última actualización: hace X”
  - Estado: `Online / Offline / Sincronizando`

### 6.2 Solo en Modo Perdido / Buscar (contexto de estrés)
Mostrar ambos:
- **Precisión cualitativa**: `Alta / Media / Baja`
- **Margen en metros**: `± Xm`
- (Opcional) motivo de baja precisión: solo si aporta valor y no ensucia (se puede reservar para Premium o solo en modo Buscar).

---

## 7) Modo sin red: fallback local (cercanía) + estimación controlada

### 7.1 Principio
- Si no hay red, **no** gastar batería intentando “encontrar el móvil” constantemente.
- La búsqueda/sincronización local se activa **solo por acción del usuario** o por **condiciones muy concretas** (ver 7.4).

### 7.2 BLE (Find Nearby — recomendado)
- Función “Find Nearby”:
  - App inicia escaneo BLE.
  - Tracker aumenta presencia BLE temporalmente.
  - UI “frío/caliente” + distancia estimada.

### 7.3 Estimación de posición cuando se corta la conectividad (sin engañar)
**Objetivo:** dar orientación durante cortes cortos sin mandar al usuario a un sitio incorrecto.

Reglas:
- La app siempre muestra el **último punto real** (`last_fix`) con su timestamp.
- Solo se permite **extrapolación corta** (posición estimada) durante una ventana breve:
  - **<= 5–10 s** (configurable por producto)
  - basada en **última velocidad/rumbo conocidos** (vector) y/o modelo simple.
- La extrapolación **siempre** se marca como:
  - trazo discontinuo + etiqueta “Estimación”
  - con **incertidumbre creciente** (círculo/radio) en metros.
- Pasada la ventana de extrapolación:
  - dejar de “mover” el marcador como si fuese real
  - mantener `last_fix` + estado “Sin cobertura” + círculo de incertidumbre (si procede).

Notas:
- Esto es UI/UX y lógica de servidor para empaquetado; no sustituye a puntos GNSS reales.
- Si el dispositivo sigue obteniendo GNSS pero no puede subirlo por celular, se guarda en buffer (store&forward) y se sincroniza después.

### 7.4 BLE Assisted Sync (opcional, rentable si se hace bien)
**Idea:** si el teléfono está cerca y el dispositivo no tiene red celular, el tracker puede enviar puntos por **BLE** a la app para:
- mostrar ubicación más actual **en el teléfono**
- y, si el teléfono tiene internet, actuar como “relay” hacia el servidor.

Reglas para no gastar batería del tracker:
- Solo activo cuando:
  - la app está **en foreground** y el usuario está en el mapa, **y**
  - el usuario ha iniciado “Buscar/Find Nearby” o “Modo Perdido”, **o**
  - el usuario activa explícitamente un toggle “Asistencia cercana (BLE)” con ventana limitada.
- Ventana limitada (ej. 2–10 min) y luego vuelve a modo normal.
- Tasa de envío por BLE adaptativa (no igual que live por LTE):
  - normal: 1 punto cada 5–15 s
  - modo perdido cercano: 1 punto cada 2–5 s

Resultado:
- Si el teléfono tiene internet: la app puede subir esos puntos al servidor como “relayed” (marcados con `source=BLE_RELAY`).
- Si el teléfono tampoco tiene internet: la app al menos pinta la ubicación en local y luego sincroniza al recuperar conexión.

### 7.5 Wi‑Fi local (opcional, solo si es imprescindible)
- Más coste energético.
- Solo activable bajo acción del usuario y con ventana limitada.

---

## 8) Contrato de endpoints (mínimo)
### 8.1 HTTP
- `GET /dogs/{dog_id}/map/now`
  - devuelve `last_fix`, puntos últimos 10–15 s, `device_state`
- `GET /dogs/{dog_id}/track/view?since=...`
  - devuelve ruta condensada + metadatos
- `GET /dogs/{dog_id}/track/refine?segment=...`
  - devuelve lote adicional de puntos para refinar

### 8.2 MQTT (solo foreground)
- Subscribe:
  - `dog/{dog_id}/location/live`
  - `dog/{dog_id}/device/state`
  - `dog/{dog_id}/alerts`

---

## 9) Reglas anti-errores (para que “no parezca roto”)
- Si no llega `now` en 1–2 s:
  - mostrar estado “Cargando ubicación…” + último punto cacheado si existe.
- Si el dispositivo está offline:
  - mostrar “Último contacto hace X” + ruta disponible.
- Si el servidor aún está procesando store&forward:
  - estado “Sincronizando ruta…” (sin bloquear mapa).

---

## 10) Checklist de validación (QA)
- Abrir mapa tras 2h: marcador actual visible en <=2 s.
- Ruta catch-up aparece progresivamente sin congelar UI.
- Sin duplicados al pasar de HTTP → MQTT.
- Caregiver con ventana activa: puede ver live; fuera de ventana, no.
- Caregiver activa Modo Perdido: notificación inmediata a Owners (push + SMS/WhatsApp si activado).
- Offline: Find Nearby BLE funciona sin quemar batería (solo bajo acción del usuario).

