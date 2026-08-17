# ARES — Bloque E: GNSS, autonomía y “verdad” en UI (Spec final v1)

## 1) Objetivo de producto (funcionalidad, no marketing)
- Meta principal: que la posición sea **normalmente <10 m** en uso real (ciudad y bosque incluidos) e intentar operar **lo más cerca posible de <5 m** cuando el entorno lo permite.
- Cuando no se pueda cumplir <10 m (multipath severo, cielo muy bloqueado, interior/metro/túnel), el sistema debe:
  - **no engañar**, y
  - ofrecer una experiencia útil para recuperar al perro (Modo Perdido + BLE).

## 2) Principio de “verdad” en UI (obligatorio)
Cada punto/tramo incluye y se persiste:
- `position_source`: `GNSS | WIFI | CELL | MIXED`
- `accuracy_m` (o estimación equivalente si la fuente no lo da)
- `fix_age_s`
- `satellites` (si aplica)
- `quality_score` (0–100, recomendado)
- flags: `is_estimated`, `is_rank_eligible`, `confidence_state`

### Mapa (estilo Google Maps)
- Marker central + **círculo de incertidumbre** (radio = `accuracy_m`).
  - cuanto peor la precisión, **más grande** el círculo
  - cuando mejora, **se cierra** el círculo
- Si la posición no es confiable, **no se muestra como pin exacto**.

## 3) Prioridad de fuentes (siempre por precisión)
Orden de preferencia:
1) `GNSS` (principal)
2) `MIXED` solo si mantiene calidad alta (`quality_score`/umbrales)
3) `WIFI` como apoyo (si se usa), siempre marcado como aproximado
4) `CELL`/torres únicamente como último recurso

### UX (decisión 4b)
- `CELL` **no se muestra por defecto** como ubicación.
- Si se implementa, solo puede mostrarse como **área aproximada** bajo toggle o en contexto controlado (no pin exacto).

## 4) Motor de calidad de posición (Position Quality Engine) — obligatorio
### Estados
- `PRECISE`: posición tratable como “pin exacto”
- `OK`: usable pero con incertidumbre visible
- `DEGRADED`: no confiable como pin exacto
- `NO_FIX`: sin fix GNSS válido

### Defaults v1 (Remote Config; ajustables)
- `precise_accuracy_max_m = 10`
- `ideal_accuracy_target_m = 5` (objetivo interno)
- `ok_accuracy_max_m = 25`
- `max_fix_age_s = 10`
- `min_sats_ok = 4`
- `min_sats_precise = 5`
- `degraded_after_s = 15` (si se mantiene mala calidad)
- `no_fix_after_s = 25–30` (sin fix válido en movimiento)

### Anti-saltos / outliers (crítico ciudad)
- Rechazar puntos que impliquen salto/velocidad imposible en ventana de 2–3 s.
- Si outlier: no mover el pin como “verdad”; marcar como `DEGRADED`.

## 5) Modo degradado (sin engaño + reglas social)
Si un punto/tramo no pasa umbrales:
- se marca `DEGRADED/NO_FIX`
- se visualiza con círculo grande y (si aplica) trazo discontinuo

### Social / rankings / rewards
- Solo cuentan tramos con calidad suficiente:
  - `GNSS` bueno
  - `MIXED` solo si cumple umbrales de calidad
- Puntos degradados se pueden ver en histórico, pero **no cuentan para competir**.

## 6) Latencia y “catch-up” (ya decidido)
### Objetivo UX
- Al abrir el mapa tras horas:
  1) primero **estado actual + últimos 10–15 s** (máxima prioridad)
  2) luego ruta orientativa
  3) refinado por tandas
- Target: mapa útil inmediato; esencial completo en ~5 s.

### Servidor
- Deduplicación y condensación server-side:
  - `device_id + boot_id + seq_id` (idempotencia)
  - apoyo por `timestamp` y distancia para deduplicación/orden

## 7) Estimación (extrapolación) en cortes
- Permitida solo como puente **≤ 5 s** desde el último fix real.
- Siempre marcada como estimación (`is_estimated=true`).
- Círculo de incertidumbre creciendo con el tiempo.
- Pasados 5 s: congelar en último fix real + estado “sin cobertura” (sin mover el pin como si fuese real).

## 8) Modo Perdido (live) — frecuencia dinámica 2–3 s
- Objetivo: máxima precisión práctica en emergencia.
- Intervalo depende de calidad y contexto:
  - si `PRECISE/OK` y buena calidad → **2 s**
  - si `DEGRADED/NO_FIX` → **3 s** (más conservador)
- Ajustable por Remote Config:
  - `lost_interval_good_s = 2`
  - `lost_interval_bad_s = 3`
- Puede ponderarse por velocidad (rápido → tender a 2 s; parado → 3 s).

## 9) Sin cobertura: Wi-Fi + “teléfono cerca” (B)
### 9.1 Wi-Fi
Usos:
1) **Power Saving Zones / Zonas seguras** (confirmación de entorno “casa”) para ahorrar batería.
2) **Backhaul**: si falla celular pero hay Wi-Fi conocida, usarla para subir estado/ruta (no como pin exacto).

Defaults v1 (Remote Config):
- `wifi_scan_interval_rest_s = 120–300`
- `wifi_scan_interval_move_s = OFF` (o muy bajo)
- `wifi_connect_window_s = 30–60`

### 9.2 Teléfono cerca: BLE Find Nearby + BLE Relay (bajo demanda)
- **BLE Find Nearby**: búsqueda frío/caliente para cerrar a metros.
- **BLE Relay**: si móvil tiene internet y collar no, el móvil sube puntos al servidor (`source=BLE_RELAY`).

Política batería tracker:
- activación por acción del usuario (Buscar / Modo Perdido / toggle)
- intentos cada **30 s** hasta **10 min**

## 10) Remote Config (sí)
- Umbrales y reglas de calidad ajustables desde backend.
- Firmware/app consultan configuración y aplican fallback a defaults si no hay conexión.
- Config versionada y firmada.

## 11) Contrato de datos (server → app) mínimo
- `lat, lon, accuracy_m, position_source, fix_age_s, satellites`
- `confidence_state (PRECISE/OK/DEGRADED/NO_FIX)`
- `quality_score`
- `is_estimated`
- `is_rank_eligible`

## 12) Validación interna (aunque no sea marketing)
Escenarios:
1) Ciudad cañón urbano
2) Ciudad abierta/parque
3) Bosque denso
4) Exterior abierto

Métricas:
- `p95_accuracy_m` por escenario
- `% tiempo en PRECISE (≤10m)` por escenario
- nº de outliers/saltos por hora

## 13) Hardware v1 / plan v2
- V1: mantener GNSS actual y maximizar con:
  - integración de antena + ventana RF
  - control EMI (LTE/DC-DC/LEDs)
  - filtros/outlier rejection
- V2 (planificado): migración a GNSS de mayor rendimiento (ideal dual-band) sin rehacer app/backend (solo fuente + tuning).

