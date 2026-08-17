# ARES — Plan de mejora futura: GNSS Dual‑Band (L1/L5) + “Precisión Extrema” (Roadmap)

## Objetivo del plan (para siguiente generación)
Subir el techo de precisión y robustez en **ciudad/bosque** reduciendo multipath y mejorando estabilidad de fix, manteniendo:
- **Verdad en UI** (círculo de incertidumbre estilo Google Maps).
- **BLE Find Nearby + BLE Relay** como cierre de precisión cuando el owner está cerca.
- Sin romper autonomía ni coste del modelo actual.

> Nota: Este plan **NO entra en v1** por coste/tiempo de validación RF/antena. Queda registrado como v2/vNext.

---

## 1) Qué aporta Dual‑Band (L1/L5) y por qué interesa
**Dual‑Band** mejora sobre todo:
- Resistencia a **multipath** (ciudad “urban canyon”).
- Estabilidad de posición en entornos difíciles.
- Mejor “confidence” (menos saltos).

No elimina límites físicos:
- **Interior/metro/túnel**: GNSS puede no estar disponible.
- Bosque muy denso: seguirá habiendo degradación, pero normalmente menos “ruidosa”.

---

## 2) Qué incluye exactamente la mejora (v2)
### 2.1 Hardware (mínimo)
- **Módulo GNSS dedicado Dual‑Band (L1/L5)** (separado del módem).
- **Antena Dual‑Band** (FPC o patch según tamaño/arquitectura).
- Front-end RF (según diseño):
  - ESD, matching, posible filtrado, ruta RF limpia.
- **Diseño EMI** reforzado para que LTE/DC‑DC/LEDs no contaminen GNSS.

### 2.2 Firmware
- Motor “Position Quality Engine” (ya definido conceptualmente):
  - `position_source` (GNSS/WIFI/CELL/MIXED)
  - `accuracy_m`, `satellites`, edad del fix
  - `quality_score` (0–100) + niveles HIGH/MED/LOW
- Rechazo de outliers y filtros anti-saltos.
- Telemetría de calidad (para tuning).

### 2.3 Backend/App
- Remote Config (umbrales ajustables sin reflashear):
  - thresholds de degradado
  - thresholds de “pin exacto”
  - reglas de elegibilidad para rankings
- UI:
  - marker + círculo de incertidumbre
  - banner de calidad (solo modo búsqueda/perdido con ±m y HIGH/MED/LOW)

---

## 3) Opciones de arquitectura GNSS para v2
### Opción A (recomendada): GNSS dedicado Dual‑Band + Antena optimizada
- Máxima mejora por euro.
- Menor dependencia del módem para GNSS.
- Más control de calidad y telemetría.

### Opción B: GNSS dual‑band + “Precisión Extrema” (modo perdido)
- Misma base de A.
- Añade un modo de emergencia con parámetros más agresivos.
- (Opcional futuro) correcciones GNSS solo en emergencia (si se decide).

---

## 4) Coste adicional estimado (BOM) — guía para decisión
> Los importes reales dependen de volumen y antena final. Esto es solo para registrar orden de magnitud.

- Módulo GNSS dual‑band: **+2€ a +10€** vs single‑band (según referencia/volumen).
- Antena dual‑band: **+1€ a +6€** (industrializada) o más si se compra “de catálogo”.
- Pasivos/RF/ESD adicionales: **+0,5€ a +2€**.
- Coste de validación/iteración: alto (tiempo/ingeniería), no BOM.

**Riesgo principal:** sin un buen diseño RF/antena, dual‑band no da la mejora esperada.

---

## 5) Requisitos de diseño (para que la mejora sea real)
### 5.1 Antena y carcasa
- “Ventana RF” (zona plástica) sin metal cercano.
- Plano de masa adecuado.
- Ubicación que minimice apantallamiento por cuerpo del perro.

### 5.2 EMI/ruido
- Separación física y eléctrica del módem LTE y DC‑DC.
- Rutado GNSS corto y limpio.
- Pruebas de interferencias en modos:
  - LEDs encendidos
  - carga/USB
  - transmisión LTE continua

### 5.3 Validación de campo (obligatoria)
Medir precisión como percentiles por entorno:
- **Open sky**
- **Ciudad densa**
- **Bosque**
- **Interior/metro** (esperar degradado; medir “comportamiento honesto”)

Métricas mínimas:
- p50/p90/p95 de `accuracy_m`
- tasa de outliers (saltos)
- estabilidad de rumbo/velocidad
- tiempo a primer fix (TTFF)
- consumo en modo normal y perdido

---

## 6) Qué no cambia (principios ARES que se mantienen)
- No “vender” torres como precisión fina:
  - CELL solo como área aproximada (si se muestra).
- Puntos degradados:
  - visibles en mapa (orientativo)
  - **no** cuentan para rankings/challenges si no pasan umbrales.
- BLE Find Nearby:
  - sigue siendo el cierre final para encontrar al perro cerca.
- BLE relay:
  - solo bajo demanda (foreground / modo perdido / toggle) con ventanas limitadas.

---

## 7) Plan de ejecución (roadmap sugerido)
### Fase 0 — Spec & selección
- Elegir módulo GNSS dual‑band candidato (2–3 finalistas).
- Definir tipo de antena (FPC vs patch) por restricciones físicas.
- Definir objetivos por entorno (KPIs).

### Fase 1 — Prototipo RF (1–2 iteraciones)
- PCBA v2 con GNSS dedicado.
- Carcasa “representativa” para tuning real.
- Primera campaña de medición.

### Fase 2 — Tuning + firmware (iterativo)
- Ajustar layout/antena/EMI.
- Refinar `quality_score` y umbrales por Remote Config.

### Fase 3 — Pre‑producción
- Validación final (ciudad/bosque).
- Bloquear BOM y reglas de UI.

---

## 8) Criterios de éxito (para aprobar v2)
- Reducción significativa de saltos y jitter en ciudad.
- Mejora del p90/p95 de `accuracy_m` (según KPIs definidos).
- Comportamiento honesto en degradado (UI + rules).
- Autonomía aceptable en modo normal (no degradar el producto).

---

## 9) Decisiones pendientes para cuando se active este plan
1) Volumen objetivo (1k / 5k / 10k+) para cerrar BOM real.
2) Restricciones de antena (espacio real / tipo).
3) Si se añade “Precisión Extrema” (solo Modo Perdido) y qué implica a nivel comercial.
