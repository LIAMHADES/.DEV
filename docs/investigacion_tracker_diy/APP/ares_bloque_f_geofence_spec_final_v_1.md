# ARES — Bloque F: Geofence (alertas fiables, cero tardanza) — Spec final v1

## F0) Objetivo
- Alertas fiables con latencia mínima cerca del borde.
- Cero engaños: evitar falsos “FUERA” por jitter.
- Batería protegida: no mantener tracking agresivo cuando está lejos, quieto y seguro.

---

## F1) Conceptos base
### Distancia clave
- `d_in_m`: distancia mínima **al borde** estando dentro (>=0).
- `d_out_m`: distancia mínima **al borde** estando fuera (>=0).

### Escala para cálculos (D_cap)
- `R_eff` (tamaño característico):
  - Círculo: `R_eff = radio`
  - Rect/Cuadrado: `R_eff = min(ancho/2, alto/2)`
- `D_cap_m`: **tope de escala** para que vallas enormes no destruyan batería.
- `S = min(R_eff, D_cap_m)`

> `S` es la “escala útil” para bandas. Si la valla es enorme, solo se considera relevante un tramo interior de tamaño `S` para definir rojo/ámbar; el resto es “deep safe” y se gobierna por movimiento + predicción.

Defaults v1 (Remote Config):
- `D_cap_m = 100`

---

## F2) Bandas dentro de la valla (Básico)
### ROJO (alto riesgo, máxima precisión)
- El ROJO **no es fijo**: se define por proporción, con techo.
- `red_m_default = min( 0.10 * S, 20m )`
- El usuario puede ajustar manualmente el ROJO (slider):
  - `red_m_user ∈ [red_m_min, 20m]`
  - `red_m_min = max(0.10 * S, 5m)` (mínimo operativo recomendado)

> La intención: en casas pequeñas el ROJO no puede ser enorme, pero tampoco ridículamente pequeño; 5m es un mínimo práctico.

### ÁMBAR (riesgo medio, tracking medio)
- El ámbar se calcula como **% de lo que queda tras el rojo**, no del total.
- `remaining = max(S - red_m_user, 0)`
- `amber_width = 0.30 * remaining`  (Básico fijo)
- `amber_limit = red_m_user + amber_width`

### SEGURA
- `d_in_m > amber_limit` → zona segura (ahorro batería).

---

## F3) Bandas dentro de la valla (Premium)
- Igual que Básico, pero:
  - `amber_pct_user ∈ [0..0.50]` (hasta 50% del remaining)
  - Permite **zonas rojas internas (hotspots)** con formas v1 (círc/rect/cuadrado) para:
    - carreteras, acantilados, zonas prohibidas, etc.
  - Hotspot rojo: forzar 2s y/o alertas específicas.

---

## F4) Intervalos de tracking (base)
### Dentro
- Zona ROJA: **2s**
- Zona ÁMBAR: **10s**
- Zona SEGURA: **30s**

### Avisos en app (decisión)
- La app **solo avisa/alerta** cuando entra en **ROJO**.
- ÁMBAR/SEGURA: sin alertas intrusivas (solo UI pasiva de color/estado).

---

## F5) Inteligencia “se dirige hacia la valla” (sube frecuencia cuando importa)
Para no fundir batería, el sistema puede subir frecuencia fuera del rojo si detecta riesgo real.

### Cálculo
- `v_toward = (d_prev - d_now) / dt` (positivo = se acerca al borde)
- `ttb = d_in_m / max(v_toward, ε)` (tiempo estimado hasta borde)

### Reglas
- Si `v_toward > 0` y `ttb < 60s`: subir 1 nivel (30→10, 10→2).
- Si `ttb < 20s`: forzar 2s.
- Si `v_toward <= 0` (se aleja): volver a intervalo base de la zona.

---

## F6) Estado FUERA (zona negra) + notificación + tracking
### Confirmación “FUERA” (para evitar jitter)
Definimos una **zona negra** fuera del borde:
- `black_out_m = 5m` (mínimo)
- Confirmación FUERA cuando:
  - `d_out_m >= max(black_out_m, 2*accuracy_m)`

### Alertas
- En el momento de confirmarse FUERA: notificación inmediata (push + SMS/WhatsApp si activado).

### Tracking estando FUERA (similar a LOST guardarraíles)
- Por defecto: **cada 5s**
- Si batería baja: **cada 10s**
- Si batería crítica: **cada 30s**

Umbrales (Remote Config, alineados con Lost):
- `low_batt_pct = 15%` → mínimo 10s
- `critical_batt_pct = 5%` → mínimo 30s

> Nota: el usuario puede cancelar/ajustar para ahorrar, pero el sistema puede imponer mínimos por batería.

---

## F7) Reposo por inmovilidad (ahorro extra)
- Si no hay movimiento significativo durante `60s` → modo reposo.
- En reposo, intervalos pueden estirarse (p.ej. 60–180s) **solo** si:
  - está en zona SEGURA, y
  - no hay riesgo por `ttb` (no se está acercando), y
  - no está en LOST_MODE.

---

## F8) Formas de geofence
- v1: Círculo / Rectángulo / Cuadrado.
- v2: Polígonos.

---

## F9) Límites por plan (activos vs guardados)
- Básico: 1 activo / 2 guardados.
- Add-on Travel: 2 activos / 5 guardados.
- Premium: 5 activos / 10 guardados.

---

## F10) Remote Config (tunable)
- `D_cap_m = 100`
- `red_pct_default = 0.10`
- `red_m_max = 20`
- `red_m_min_floor = 5`
- `amber_pct_basic = 0.30`
- `amber_pct_premium_max = 0.50`
- `black_out_m = 5`
- `ttb_boost_10s = 60s`
- `ttb_boost_2s = 20s`
- `low_batt_pct = 15`
- `critical_batt_pct = 5`
- `out_interval_default = 5s`
- `out_interval_low = 10s`
- `out_interval_critical = 30s`
- `rest_after_s = 60`

