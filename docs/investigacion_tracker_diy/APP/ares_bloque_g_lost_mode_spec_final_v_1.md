# ARES — Bloque G: LOST_MODE (recuperación real + guardarraíles) — Spec final v1

## 1) Activación, presets y extensiones
- Presets: **15 / 30 / 60 min**.
- Default al activar: **15 min**.
- Extensión:
  - Al acercarse el final, la app pregunta si necesita más: **+15 min** o **+30 min**.
  - **Ilimitadas** extensiones (sin límite de veces).
- Desactivación:
  - El usuario puede **desactivar LOST_MODE** en cualquier momento para ahorrar batería.

## 2) Selector de frecuencia (solo LOST_MODE)
- El usuario puede elegir **cada cuánto recibir ubicación** solo dentro de LOST_MODE.
- Opciones UI:
  - **Auto (recomendado)**: el sistema decide intervalos dinámicos (2–3 s) en función de velocidad, calidad y batería.
  - **5 s / 10 s / 30 s**.
- Guardarraíl batería (forzado por sistema):
  - Si batería <= **15%** ⇒ mínimo **10 s** (perfil Low Power).
  - Si batería <= **5%** ⇒ mínimo **30 s** (perfil Critical).
  - La app muestra: “Limitado por batería para aguantar más tiempo”.

## 3) Frecuencia dinámica dentro de LOST_MODE
- Objetivo: máxima precisión práctica sin agotar batería de forma absurda.
- En **Auto**:
  - Buena calidad + alta velocidad ⇒ **2 s**.
  - Calidad/media/velocidad media ⇒ **3 s**.
  - Si entra en Low Power/Critical, se respetan mínimos (10 s / 30 s).

### Remote Config (mínimo)
- `lost_interval_fast_s=2`
- `lost_interval_normal_s=3`
- `lost_interval_low_batt_s=10`
- `lost_interval_critical_batt_s=30`
- `low_batt_pct=15`
- `critical_batt_pct=5`
- Umbrales de calidad (ver Bloque E): `precise_accuracy_max_m`, `ok_accuracy_max_m`, `min_sats_*`, `max_fix_age_s`, etc.

## 4) Backend: batería baja/crítica (no se apaga LOST_MODE, se optimiza)
- **LOW (<=15%)**:
  - Mantiene comunicación, entra en perfil “Lost Low Power”.
  - Intervalo mínimo: **10 s**.
  - Reduce lo no esencial (Wi-Fi scanning agresivo, BLE relay automático, extras).
- **CRITICAL (<=5%)**:
  - Mantiene comunicación hasta agotar batería.
  - Intervalo mínimo: **30 s**.
  - Mensajes compactos + evitar loops caros.

## 5) LED pattern en LOST_MODE
- Patrón SOS (Morse) disponible: `... --- ...`.
- **Decisión:** **solo se activa si el usuario lo activa** (no automático).
- En Low/Critical, el sistema puede reducir duty/brillo si compromete supervivencia.

## 6) UX de recuperación (mapa + verdad)
- En LOST_MODE, el mapa prioriza:
  1) **estado actual + últimos 10–15 s**
  2) ruta orientativa
  3) refinado posterior
- Banner en modo búsqueda:
  - Calidad: `±Xm` + círculo de incertidumbre.
  - Perfil actual: Normal / Low Power / Critical.
  - Autonomía estimada en LOST_MODE.

## 7) Teléfono cerca (casos extremos)
- **BLE Find Nearby** (frío/caliente) para cerrar la búsqueda a metros.
- **BLE Relay** bajo demanda para frescura (si el móvil tiene internet y el collar no).
- Política batería tracker:
  - activación por acción del usuario (Buscar / toggle)
  - intentos cada **30 s** hasta **10 min**

## 8) Roles y notificaciones
- Owner: siempre puede activar/desactivar/extender.
- Caregiver/invitado (si tiene permiso): puede activar LOST_MODE.
  - Notifica inmediatamente a Owners (push y SMS/WhatsApp si están activados).

## 9) Estimación de autonomía en app (modelo v1)
### Datos
- Batería (v1 Medium): **2750 mAh**.
- Consumo de referencia aportado: **~150 mA** cuando la frecuencia es **10 s**.

### Regla de cálculo (v1, explícita y ajustable)
- Para dar una estimación simple al usuario, el modelo v1 usa la aproximación:
  - `I_avg(10s) = 150 mA` (ancla)
  - `I_avg(30s) ≈ 50 mA` (aprox. por proporcionalidad de intervalo; se refina con telemetría real)
  - `I_avg(5s) ≈ 300 mA` (solo como aproximación; se refina con telemetría)
- La app muestra la autonomía como **estimación** y se recalcula al recibir telemetría real.

### Duración estimada desde umbrales (con el modelo v1)
- 15% de 2750 mAh = **412.5 mAh**
- 5% de 2750 mAh = **137.5 mAh**

**Con reglas de sistema (15%→10s, 5%→30s):**
- Tramo 15%→5% (275 mAh) a 150 mA ⇒ **~1.83 h**
- Tramo 5%→0% (137.5 mAh) a 50 mA ⇒ **~2.75 h**
- Total desde 15% hasta 0% ⇒ **~4.6 h**

> Nota: estos números se refinan automáticamente cuando haya telemetría real de consumo (TX retries, time-to-fix, etc.).

## 10) Telemetría mínima para refinar autonomía (recomendado)
- `gnss_on_time_s`
- `time_to_fix_avg_s`
- `tx_on_time_s`
- `tx_retries_count`
- `signal_quality` (CSQ u otro)

Con esto el backend puede ajustar el modelo de autonomía por entorno/cobertura sin actualizar app/firmware.

