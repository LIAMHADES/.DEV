# ARES — Escalabilidad de Precios, Márgenes y Seguro (v2.0)

**Versión:** 2.0 | **Fecha:** 2026-08-14 | **Estado:** documento vivo — se actualiza con cada cambio de coste, precio o volumen

> **Cambio v1.0 → v2.0 (2026-08-14):**
> - Precios hardware revisados a la baja: Medium **120€**, Large **149€**, Family Pack **desde 199€** (2× Medium, cualquier combinación) — desde 139/159/249€.
> - Seguro escalonado en 2 opciones: **+2 años = 19,99€** · **+3 años = 25€**.
> - Modelo de impuestos España añadido (IVA 21% + IRPF/Sociedades ~25% → carga ~50%).
> - Posicionamiento confirmado: **salud/nutrición es el diferencial** (no el enganche de goma).
> - Producción de arranque: **50 unidades**.

> Este documento registra **cómo deben adaptarse precios, márgenes y el seguro del dispositivo** a medida que ARES crece (poca producción → preventa → escala industrial). Es la referencia para no tomar decisiones de precio a ciegas y para saber **qué hay que re-ajustar** cuando cambian los costes.

---

## 1. POR QUÉ EXISTE ESTE DOCUMENTO

- Los precios y el seguro actuales están fijados para **producción baja/preventa** (~50 uds de arranque, escalando a 100).
- Cuando ARES escale (1.000+, 5.000+ uds), el **coste de hardware baja** (~65€ → ~45€/u según roadmap) y eso cambia:
  - el margen bruto,
  - el coste real de reposición del seguro (el 50% del dispositivo),
  - la competitividad frente a competencia que también baja precios (Weenect, Kippy, etc.).
- Este documento es el **contrato interno** de qué hay que revisar y cuándo. No se edita por impulso: se actualiza con decisión y log (DL-XXX).

---

## 2. MARGENES ACTUALES (Precios v2.0 — 50 uds de arranque)

| Modelo | Coste HW | PVP | Margen Bruto (antes impuestos) | Notas |
|---|---|---|---|---|
| ARES Medium | ~64€ | **120€** | ~56€ (87%) | Tracker 2750mAh + Plan Esencial |
| ARES Large | ~67€ | **149€** | ~82€ (122%) | Tracker 4000mAh + Plan Plata 12m |
| Family Pack (cualquier combo) | ~128€ (2× M) | **desde 199€** (2× Medium) | ~71€ (36%) min | Descuento por 2 suscripciones; combinaciones: 199€/224€/249€ |

**Nota sobre el margen tras impuestos (España):** el margen bruto de la tabla es ANTES de impuestos. Tras IVA (21%) + IRPF/Sociedades (~25%), la rentabilidad neta real por unidad es menor — ver §3.

**Puntos de inflexión del coste por volumen (roadmap):**

| Volumen | Coste HW/u aprox. | Referencia |
|---|---|---|
| **50 uds (arranque)** | ~65€ | BOM actual |
| ~100 uds (fase certificación CE) | ~60€ | DL-012 |
| 1.000+ uds (industrial) | ~45€ | MES 6 roadmap |
| 5.000+ uds | ~45€ (negociación adicional) | MES 12 |

> **Regla:** cada vez que baje el coste de hardware, hay que decidir SI baja el PVP (competir), SE MANTIENE (sube margen), o se invierte el margen extra en features/garantía. Decisión explícita, nunca automática.

---

## 3. IMPUESTOS EN ESPAÑA (cómo afectan al precio y al margen)

### 3.1. Carga fiscal real (revisado 2026-08-14)

La fiscalidad en España para venta directa de hardware se compone de **dos impuestos en cadena**, no uno:

| Impuesto | Tipo | Sobre qué | Efecto en el precio |
|---|---|---|---|
| **IVA** | 21% | Sobre el PVP final | Lo paga el cliente; tú lo recaudas y lo ingresas a Hacienda. Neutral a nivel de margen, pero **encarece el precio visible** que compara el comprador. |
| **IRPF (autónomo) / Impuesto de Sociedades** | ~25% | Sobre el **beneficio neto** (ingresos − costes − IVA) | Es el impuesto real sobre el margen. |
| **Cuota de autónomos** | ~300€/mes fijos | Gasto fijo mensual | No es porcentual, pero es un coste fijo relevante a bajo volumen. |

**Carga fiscal combinada ≈ 50%** (21% IVA + ~25% sobre beneficio). Es de donde sale tu referencia del "50% de impuestos".

### 3.2. Cómo calcular el PVP mínimo con margen de reinversión del 30%

**Definición (confirmada con el usuario):** el 30% es lo que queda **después** de impuestos, disponible para reinvertir. Por tanto, antes de IRPF necesitas un margen bruto mayor.

```
Beneficio neto = (PVP sin IVA − coste total) × (1 − 0,25)
Objetivo: beneficio neto ≥ 30% de lo que queda tras costes
Equivale a: margen bruto antes de impuestos ≥ 40% sobre el coste total
(40% × 0,75 = 30% neto)
```

**Coste total por unidad (50 uds, venta directa + fulfillment):**

| Concepto | Medium | Large |
|---|---|---|
| Producción | 64€ | 67€ |
| FBA fulfillment + envío inbound `[EST]` | 5€ | 5€ |
| **Coste total** | **69€** | **72€** |

**PVP mínimo para margen neto ≥30% (tras IVA 21% + IRPF 25%):**

| Modelo | Coste | Margen bruto 40% | PVP sin IVA | **PVP con IVA 21%** |
|---|---|---|---|---|
| Medium | 69€ | 27,60€ | 96,60€ | **~117€** |
| Large | 72€ | 28,80€ | 100,80€ | **~122€** |

> **Conclusión a 50 uds:** el PVP mínimo viable es **~117€ (Medium)** y **~122€ (Large)** con IVA incluido. Los precios fijados en v2.0 (**120€ / 149€**) están por encima de ese suelo, así que cumplen con el margen de reinversión del 30% tras impuestos. [OK] 

### 3.3. Sensibilidad al coste de producción

| Volumen | Coste HW | Coste total | PVP Medium actual | Margen neto tras impuestos |
|---|---|---|---|---|
| 50 uds | 65€ | 69€ | 120€ | ~31% [OK]  (justo en el umbral) |
| 100 uds | 60€ | 65€ | 120€ | ~41% [OK]  |
| 1.000+ uds | 45€ | 50€ | 120€ | ~61% [OK]  |

---

## 4. PRECIOS DE LA SUSCRIPCIÓN (planes)

Precios **v2.1 (2026-08-14)** — ver `ARES_planes_basico_vs_premium_v1.md`:

| Plan | Precio | Posición |
|---|---|---|
| Esencial | **6€/mes** (60€/año) | Tier de entrada, historial 7 días |
| Básico | **10€/mes** (100€/año) | Historial 30 días, 5 zonas, 5 compartidos, informe mensual |
| Premium | **12,99€/mes** (129,90€/año) | Informe semanal + estadísticas diarias, nutrición IA, historial 1 año |

### 4.1. Técnica de anclaje (anchoring) — aplicada

- **Esencial→Básico:** +4€/mes — justificado por historial 30 días, 5 zonas, 5 compartidos e informe mensual de salud.
- **Básico→Premium:** +2,99€/mes — el salto se percibe pequeño frente al mucho más valor de Premium (informe semanal, nutrición IA, multi-mascota, IA de fatiga). **Empuja a Premium.**
- El Premium a 12,99€ usa el anclaje psicológico del "9" (como los precios 99).

### 4.2. Costes de servicio de las suscripciones (el gap que faltaba)

> Añadido 2026-08-14. El margen documentado antes solo contaba la SIM. Los costes reales del servicio incluyen **nube, pasarela, notificaciones, mapas, soporte y amortización de la app**. Tabla de **coste medio / máximo por cliente-mes**:

| Concepto | Esencial (6€) | Básico (10€) | Premium (12,99€) |
|---|---|---|---|
| SIM + datos (1NCE) | ~0,02€ | ~0,05€ | ~0,10€ |
| Nube/hosting backend (VPS+DB) | 0,30-0,80€ | 0,40-1,00€ | 0,50-1,50€ |
| Pasarela de pago (Stripe ~2,9%+0,25) | ~0,42€ | ~0,54€ | ~0,63€ |
| Push notifications (Firebase) | ~0,05€ | ~0,08€ | ~0,10€ |
| Mapas (Google Maps/Mapbox, historial) | ~0,10€ | ~0,30€ | ~0,50€ |
| Soporte al cliente | 0,30-0,80€ | 0,40-1,00€ | 0,50-1,20€ |
| Amortización app/backend (30k€ ÷ 3a ÷ 1000 clientes) | ~0,83€ | ~0,83€ | ~0,83€ |
| **Coste total MEDIO** | **~2,00€** | **~2,60€** | **~3,70€** |
| **Coste total MÁXIMO (arranque 100 clientes)** | **~2,90€** | **~3,80€** | **~4,90€** |

> `[EST]` — los costes de nube/soporte caen mucho con volumen (a 5.000 clientes la nube baja a ~0,10€/cliente). El coste fijo es el problema del arranque (50-100 clientes).

### 4.3. Margen neto por plan (tras ~35% de carga fiscal media: IVA 21% + IRPF/IS ~25%)

**A 1.000+ clientes (coste medio):**

| Plan | Precio | Coste medio | Margen bruto | Margen neto | % |
|---|---|---|---|---|---|
| Esencial | 6€ | 2,00€ | 4,00€ | **2,60€** | 43% |
| Básico | 10€ | 2,60€ | 7,40€ | **4,81€** | 48% |
| Premium | 12,99€ | 3,70€ | 9,29€ | **6,04€** | 46% |

**A 100 clientes (arranque, coste máximo):**

| Plan | Precio | Coste máx | Margen bruto | Margen neto | % |
|---|---|---|---|---|---|
| Esencial | 6€ | 2,90€ | 3,10€ | **2,02€** | 34% |
| Básico | 10€ | 3,80€ | 6,20€ | **4,03€** | 40% |
| Premium | 12,99€ | 4,90€ | 8,09€ | **5,26€** | 40% |

> **Conclusión:** a 6€/10€/12,99€ los márgenes netos son sanos (34-48%) incluso en el peor caso de arranque. El Esencial a 5€ daría ~27% (fino); a 6€ da 34% — por eso se fija en 6€.

### 4.4. App Store / Google Play (por qué pagar SIEMPRE por web)

- **Apple/Google cobran 15% (small business) o 30%** de cada suscripción si se paga in-app → 0,90-3,90€/mes de cada plan se van en comisión.
- **Solución:** el pago se hace SIEMPRE vía **web** (Stripe/plataforma propia), no in-app. La app solo usa el login. Esto **ahorra 0,90-3,90€/mes por cliente** y es decisión estratégica confirmada.
- Ojo: Apple/Google exigen que las suscripciones digitales se paguen in-app si se consumen dentro de la app; hay que estructurarlo como "cuenta web + acceso app" para mantenerse en los márgenes permitidos (requiere validación legal/comercial al implementar).

---

## 5. POSICIONAMIENTO — EL DIFERENCIAL NO ES EL ENGANCHE DE GOMA

**Confirmado 2026-08-14:** el enganche de goma NO es un diferenciador comercial. ARES debe apalancarse sobre lo que realmente la diferencia (alineado con DL-001):

- **Nutrición y cálculo de calorías** — dieta personalizada según actividad real + macros (Premium).
- **Ejercicio real anti-trampa** — IMU que distingue pasos de viaje en coche (la "comida"/ejercicio real).
- **Descanso y detección de anomalías** — cambio de comportamiento como primera señal de que algo va mal.
- **Preocupación real por la salud** — "saber si está bien, no solo dónde está".

**Consecuencia:** el mensaje de venta se centra en **salud/nutrición/ejercicio/descanso**, y la localización GPS pasa a ser la funcionalidad de seguridad que acompaña (no el argumento principal). El enganche de goma es un detalle de diseño, no un claim de marketing.

---

## 6. SEGURO DEL DISPOSITIVO

### 6.1. Modelo escalonado (fijado 2026-08-14)

| Opción | Precio | Cobertura total (España, garantía legal 2 años) | Notas |
|---|---|---|---|
| **+2 años** | **19,99€** pago único | **5 años** (2 garantía + 2 seguro) | Opción recomendada por defecto |
| **+3 años** | **25€** pago único | **6 años** (2 garantía + 3 seguro) | Para quien quiere máxima tranquilidad |

> **Nota legal:** la duración de la garantía legal varía por país (en España la garantía vigente es de **3 años** desde 2022 para bienes nuevos; en otros países puede ser 2). El seguro **arranca al terminar la garantía legal local**, así el cliente nunca queda sin cobertura. Si contamos la garantía de 3 años (España): +2 años de seguro = 5 años totales, +3 años = 6 años.

**Parámetros del seguro:**

| Parámetro | Valor |
|---|---|
| Cobertura | Roturas/faltas no cubiertas por garantía legal |
| Reposición | Cliente paga **50% del precio del dispositivo nuevo** |
| Gestión | Póliza + recordatorios desde la app |
| Siniestralidad estimada | ~10%/año `[EST]` — sustituir por dato real cuando haya clientes |

### 6.2. La lógica del precio (por qué 19,99€ / 25€)

- **Antes (39,90€):** cliente pagaba 39,90 + 69,50 (50% de 139€) = 109,40€ frente a 139€ → **solo ahorraba ~30€**. Mala percepción.
- **Ahora (19,99€, con hardware a 120€):** 19,99 + 60 (50% de 120€) = 79,99€ frente a 120€ → **ahorra ~40€**. Percepción clara de valor.
- **Con +3 años (25€):** 25 + 60 = 85€ frente a 120€ → **ahorra ~35€** por más cobertura.
- **Rentabilidad:** con siniestralidad ~10%/año, el coste esperado de la opción de 2 años ≈ 60 × 0,20 = **~12€**. Con 19,99€ queda margen sano. `[EST]`
- 19,99€ es un precio psicológico (<20€); 25€ sigue siendo trivial frente al ahorro percibido.

### 6.3. Qué revisar cuando escale (obligatorio)

Cuando el coste de hardware baje (ej. a 45€), el **50% de reposición también baja** (~60€ → ~50-52€ si se re-preciase el hardware). En ese momento hay que decidir:

1. **¿Baja el precio del seguro?** Si la reposición es más barata, se puede mantener 19,99/25€ (más margen) o bajar a 14,99€ (más agresivo).
2. **¿Baja el % de reposición?** Mantener 50% o subir a 40% (más favorable al cliente).
3. **¿Ampliar cobertura?** Añadir pérdida/robo (complica el riesgo y requiere verificación).
4. **Siniestralidad real:** cuando haya datos de clientes reales, sustituir el `[EST]` de 10%/año por la cifra real y re-calcular la rentabilidad.

---

## 7. LO QUE HAY QUE ADAPTAR EN EL FUTURO (checklist vivo)

> Cada punto se marca [[OK]  decidido] / [⏳ pendiente] con fecha. No se eliminan, se actualizan.

| # | Elemento | Qué cambia al escalar | Estado |
|---|---|---|---|
| 1 | Coste hardware | ~65€ → ~45€/u a 1.000+ uds | ⏳ pendiente (roadmap MES 6) |
| 2 | PVP hardware | **Decidido v2.0: 120€/149€ · Family Pack desde 199€** (2×M 199 / M+L 224 / 2×L 249). Revisar cuando baje el coste | [OK]  decidido 2026-08-14 |
| 3 | Precio del seguro | Revisar 19,99/25€ y % de reposición cuando baje el coste | ⏳ pendiente (ver §6.3) |
| 4 | Precio del Básico | **Decidido v2.1: 10€/mes** (historial 30 días, 5 zonas, 5 compartidos, informe mensual + benchmarks, dietas/peso, guía de alimentos, informe batería, exportación PDF) | [OK]  decidido 2026-08-14 |
| 5 | Precio del Premium | **Decidido v2.1: 12,99€/mes** (informe semanal + estadísticas diarias) | [OK]  decidido 2026-08-14 |
| 6 | Plan Esencial | **Decidido v2.1: 6€/mes** (historial 7 días). Suelo real = coste de conectividad (~1,25-2€/mes) | [OK]  decidido 2026-08-14 |
| 7 | Certificaciones (RED/ROHS/EMC) | ~4.800€ una vez — impacta margen de los primeros lotes | ⏳ fase 3 |
| 8 | Competencia | Weenect bajó a ~32-46€; Kippy similar. Re-evaluar posicionamiento | ⏳ periódico |
| 9 | Coste SIM/1NCE | Permanencia 12 meses por SIM; re-negociar a volumen | ⏳ pendiente |
| 10 | Partner de seguro | Fijar anexo de póliza con coberturas exactas | ⏳ pendiente (RR pendiente) |
| 11 | Garantía legal por país | Duración varía (España 3 años desde 2022); el seguro arranca al terminar la garantía local | ⏳ adaptar por mercado |
| 12 | Siniestralidad real del seguro | Sustituir estimación por datos reales de clientes | ⏳ cuando haya clientes |
| 13 | Impuestos (IVA 21% + IRPF/IS 25%) | Recalcular margen neto cuando cambien tipos o forma jurídica | ⏳ revisar en 2027 |
| 14 | Programa early adopters | Prometer mensualidades gratis futuras a primeros clientes cuando bajen precios | ⏳ al lanzar (coste est. 6 meses × 100 clientes ≈ 1.050€) |
| 15 | Reposicionamiento salud/nutrición | Mantener el mensaje de "cómo está", no solo "dónde está" | [OK]  decidido 2026-08-14 |
| 16 | Costes de servicio de suscripción | Documentados (§4.2): nube, pasarela, push, mapas, soporte, amortización. Recalcular con volumen real | [OK]  documentado 2026-08-14 |
| 17 | Pago siempre por web | Evitar 15-30% App Store/Google Play | [OK]  decidido 2026-08-14 |
| 18 | Features futuras Premium (recordatorios vacunas/pulgas + lector calidad de comida) | Analizar coste/valor (ver §11); NO implementar aún | ⏳ futuro |
| 19 | Tienda integrada (dropshipping/afiliación) | **Planificada**: ARES no guarda stock, redirige a la marca y cobra comisión. Requiere curaduría + partners. Plan en `ARES_Tienda_Integrada_Bienestar.md` | ⏳ planificada 2026-08-14 |
| 20 | Aviso de alejamiento por BLE | **Descartada** — RSSI poco fiable con obstáculos, requiere conexión continua y consume batería del collar; riesgo de avisos falsos. No se implementa. | [OK]  descartada 2026-08-14 |
| 21 | Alertas SMS/WhatsApp | **No es diferenciador core** (WhatsApp necesita internet, SMS cobertura). No se destaca en pricing | [OK]  decidido 2026-08-14 |
| 22 | Features salud/seguridad nuevas | **Básico:** score de bienestar diario, registro de medicación, guía de ejercicio, **alerta de golpe de calor (índice térmico)**, **recomendación de agua según datos del perro**. **Premium:** chat veterinario, plan preventivo, modo cachorro/senior, análisis rascado/ladridos (sin ansiedad por separación) | [OK]  aprobadas 2026-08-14 |

---

## 8. REGLAS DE DECISIÓN (cómo usar este documento)

1. **Nunca cambiar un precio sin anotarlo aquí** (y en el log de decisiones DL-XXX).
2. **Cada descenso de coste de hardware dispara la revisión** de: PVP, seguro y % de reposición.
3. **El Básico no sube hasta que el valor percibido suba primero.** (Aplicado: el Básico a 10€ incluye historial 30 días, 5 zonas, 5 compartidos e informe mensual.)
4. **Competir ≠ bajar siempre:** ARES no gana en precio puro (BOM 64€ vs ~20-25€ de Tractive/Weenect a escala). Gana en **salud/nutrición** (calorías, dieta, ejercicio anti-trampa, descanso) — apalancarse en eso, no en bajar precios.
5. **El seguro no debe percibirse como "pagas 40 y ahorras 30":** la regla es que el ahorro del cliente sea siempre sustancial (≥35€) y el margen del seguro sano (≥25% sobre siniestralidad esperada).
6. **El margen de reinversión del 30% se calcula tras impuestos** (IVA 21% + IRPF/IS 25%). A 50 uds el suelo es ~117€ (Medium); los precios v2.0 (120/149€) lo cumplen.
7. **El coste de la suscripción no es solo la SIM:** siempre calcular margen incluyendo nube, pasarela, notificaciones, mapas, soporte y amortización (ver §4.2).
8. **Pago siempre por web:** evita el 15-30% de App Store/Google Play (ahorro de 0,90-3,90€/mes por cliente).

---

## 9. HISTORIAL DE CAMBIOS

| Fecha | Cambio | Justificación | Log |
|---|---|---|---|
| 2026-08-14 | Seguro: 39,90€ → 19,99€ (1 opción) | A 39,90€ el cliente solo ahorraba ~30€. A 19,99€ ahorra ~40-50€ y la póliza mantiene margen sano. | — |
| 2026-08-14 | Seguro escalonado: +2a=19,99€ · +3a=25€ | Decisión usuario: cobertura escalada (5-6 años totales). | — |
| 2026-08-14 | PVP hardware: 139/159/249€ → **120/149€ + Family Pack desde 199€** | Redondear hacia arriba el suelo viable (117/122€) con margen de reinversión 30% tras impuestos. Family Pack flexible (cualquier combinación) con descuento por pack al generar 2 suscripciones. | — |
| 2026-08-14 | Impuestos España documentados | IVA 21% + IRPF/IS 25% = carga ~50%; modelo de PVP mínimo añadido. | — |
| 2026-08-14 | Posicionamiento: diferencial = salud/nutrición | El enganche de goma NO es diferenciador. Alineado con DL-001. | — |
| 2026-08-14 | Early adopters: mensualidades gratis futuras | A los primeros clientes se les promete meses gratis cuando bajen precios. Coste est. ~1.050€ (6 meses × 100). | ⏳ al lanzar |
| 2026-08-14 | Suscripción v2.1: **6€/10€/12,99€** (antes 6/10/16€) | Comparativa con competencia (rango 3-13€): Esencial 6€, Básico 10€ (con 30 días historial + informe mensual), Premium 12,99€ (informe semanal + estadísticas diarias). Anclaje Básico→Premium = +2,99€. | — |
| 2026-08-14 | Básico ampliado: historial 30d, 5 zonas, 5 compartidos, informe mensual | Para justificar el salto 6→10€ (valor real vs Esencial). | — |
| 2026-08-14 | Costes de servicio de suscripción documentados (§4.2) | Nube, pasarela, push, mapas, soporte, amortización — el gap que solo contaba la SIM. Márgenes 34-48% netos a 6/10/12,99€. | — |
| 2026-08-14 | Pago siempre por web | Evita 15-30% de App Store/Google Play. Ahorro 0,90-3,90€/mes/cliente. | — |
| 2026-08-14 | §11: análisis features futuras Premium | Recordatorios de cuidados (vacunas/pulgas) y lector de calidad de comida — coste/valor evaluado, NO implementar aún. | ⏳ futuro |
| 2026-08-14 | Básico ampliado (2ª ronda): benchmarks, dietas/peso, guía de alimentos, informe batería, exportación PDF | Más valor tangible al Básico; el Premium conserva IA + comunidad. | — |
| 2026-08-14 | Premium ampliado: superalimentos + aviso de peligros de la zona | Contenido exclusivo de nutrición y seguridad local según estación/ubicación. | — |
| 2026-08-14 | Tienda integrada descartada del lanzamiento | Sin BD de productos ni certificación de calidad. Futuro (contenido/partners). | [OK]  descartada |
| 2026-08-14 | Alertas SMS/WhatsApp fuera del pricing destacado | No es diferenciador (WhatsApp=internet, SMS=cobertura). | [OK]  decidido |
| 2026-08-14 | §11.4: aviso de alejamiento BLE sin internet | Modo de proximidad BLE para rutas (alcance ~100m), coste ~0. Futuro. | ⏳ futuro |
| 2026-08-14 | BLE de alejamiento **DESCARTADO** | Señal poco fiable con obstáculos, requiere conexión continua, consume batería. Riesgo de avisos falsos. | [OK]  descartado |
| 2026-08-14 | Tienda integrada → plan de dropshipping/afiliación | Nuevo doc `ARES_Tienda_Integrada_Bienestar.md`: ARES no guarda stock, redirige a la marca, comisión. | ⏳ planificada |
| 2026-08-14 | Features salud/seguridad nuevas aprobadas | Básico: score bienestar, medicación, guía ejercicio. Premium: chat veterinario, plan preventivo, golpe de calor, cachorro/senior, rascado/ladridos (sin ansiedad separación). | [OK]  aprobadas |

---

## 10. FUENTES

- `01_PRODUCTO_Y_NEGOCIO.md` — márgenes, roadmap, PVP, log de decisiones DL-001..013
- `ARES_planes_basico_vs_premium_v1.md` — estructura de planes
- `ARES_Especificacion_Pagina_Pricing_v1.md` — página de precios
- `ARES_Risk_Register_v1.md` — riesgos (incl. RR sobre coberturas de seguro pendientes)
- `Análisis Competitivo de Localizadores GPS para Perros (Europa).md` — precios de competencia

---

## 11. FEATURES FUTURAS PREMIUM — ANÁLISIS DE COSTES Y VALOR (2026-08-14)

> Análisis de valor para 2 features propuestas por el usuario para Premium. **NO se implementan aún** — solo se evalúa coste y valor para decidir más adelante. También abren vías de partnership (veterinarios, marcas de alimento/antiparasitarios).

### 11.1. Recordatorios de cuidados del perro (vacunas, pastillas, collares antipulgas)

**Qué es:** el sistema avisa cuándo toca cada cuidado (vacunas según calendario/raza/edad, desparasitación, collares antipulgas, revisión veterinaria), con recordatorios en app.

**Coste `[EST]`:** mínimo — es lógica de calendario + notificaciones push ya existentes. ~0€/mes de infraestructura. Requiere una **base de datos de calendarios de vacunación por raza/edad** (contenido médico, a validar con veterinario) — coste de contenido, no de tecnología.

**Valor para el usuario:**
- Muy alto en **percepción de cuidado** ("ARES se acuerda de lo importante").
- Ahorra el olvido de antiparasitarios → protección real del perro (garrapatas, pulgas).
- Diferencial: ningún competidor de la franja 5-13€ lo ofrece de serie.

**Valor para ARES (futuro):**
- **Partnership con veterinarios:** la app puede recomendar/citar el veterinario → acuerdo de derivación/afiliación.
- **Partnership con marcas:** al avisar "toca collera antipulgas", puedes recomendar producto de marca partner con comisión (afiliado) o cupón.
- **Retención:** un recordatorio útil cada X semanas = motivo para abrir la app → reduce churn.

**Riesgo:** responsabilidad médica — los recordatorios deben presentarse como "recomendación, consulte a su veterinario". Validar contenido con un veterinario antes de publicar.

**Veredicto:** ✅ **Alto valor / coste casi nulo** — prioridad alta para una futura iteración Premium. El contenido médico es el único trabajo real.

### 11.2. Lector de calidad de comida (no solo comida preparada)

**Qué es:** el usuario fotografía o escanea el alimento de su perro (croquetas, comida húmeda, **o comida natural/casera preparada**) y la app lee/analiza la calidad nutricional (ingredientes, macros, adecuación a su perro).

**Coste `[EST]`:**
- **IA de visión** (reconocer el alimento por foto): API de visión (Gemini/Claude multimodal) — ~0,01-0,05€ por foto analizada. Si cada usuario analiza ~5-10 alimentos/año → ~0,10-0,50€/cliente/año. `[EST]`
- **Base de datos de alimentos** (marcas comerciales + valores nutricionales): trabajo de contenido, similar a la de Dog Fuel ya planeada.
- **Comida natural/casera:** no hay base de datos — requiere un **motor de estimación por ingredientes** ("peso, proteína, grasa, carbohidrato" calculados desde lo que el dueño declara o fotografía). Más complejo de calibrar.

**Valor para el usuario:**
- Muy alto: responde la pregunta más común de los dueños ("¿le estoy dando la comida correcta?").
- Diferencia Premium de forma clara (nadie en la franja lo ofrece).
- La parte de "comida natural/casera" es **única** — la competencia solo escanea productos comerciales.

**Valor para ARES (futuro):**
- **Partnership con marcas de pienso:** si la app recomienda "esta marca cubre mejor la proteína", se puede monetizar por afiliado/colocación.
- Tienda integrada (ya planeada) con recomendaciones → upsell.
- Retención: análisis periódico = apertura recurrente de app.

**Riesgo:** exactitud nutricional — una recomendación errónea de dieta puede ser dañina. Requiere validación veterinaria del motor de estimación.

**Veredicto:** ⚠️ **Alto valor pero coste/riesgo medio** — implementar primero la parte de alimentos comerciales (base de datos + escáner, más segura), y la comida natural/casera como fase 2 con validación veterinaria.

### 11.3. Resumen y recomendación

| Feature | Coste `[EST]` | Valor usuario | Valor negocio (partnership) | Riesgo | Prioridad futura |
|---|---|---|---|---|---|
| Recordatorios de cuidados | ~0€ + contenido médico | Alto | Alto (vet + marcas) | Bajo (con disclaimer) | 🥇 Alta |
| Lector de comida (comercial) | ~0,10-0,50€/cliente/año | Muy alto | Alto (marcas pienso) | Medio | 🥈 Media-alta |
| Lector de comida (natural/casera) | Mayor (motor + calibración) | Único | Alto | Medio-alto | 🥉 Fase 2 |

**Conclusión:** ambas features refuerzan el posicionamiento **salud/nutrición** (el diferencial real de ARES) y abren vías de partnership. Se añadirán como **roadmap Premium futuro**, no en el lanzamiento. Decisión de implementación: cuando la base de clientes justifique el coste de contenido veterinario.

### 11.4. Aviso de alejamiento por BLE (dispositivo↔teléfono, SIN internet/cobertura)

**Pregunta del usuario:** ¿se puede avisar al propietario cuando el perro se aleja X metros usando la comunicación dispositivo-teléfono, sin depender de internet ni cobertura (terceros)?

**Respuesta: SÍ, técnicamente viable y de coste casi nulo — pero con límites físicos.**

- **Mecanismo:** el collar y el teléfono ya tienen **BLE** (configuración, Find Nearby, Phone-Assist). BLE es un enlace **punto a punto directo** — no necesita internet ni torres de telefonía. El collar puede medir la fuerza de señal (RSSI) y avisar si el perro se aleja.
- **Alcance real:** BLE en campo abierto llega a **~50-100 m** (mejor en línea recta, peor en ciudad). Es un "modo de proximidad", no un seguimiento de kilómetros.
- **Sin coste de terceros:** al ser directo dispositivo↔teléfono, **no hay coste de datos ni de SMS**. Solo consume algo más de batería en el collar mientras el modo está activo. `[EST]` despreciable si se activa solo en rutas.
- **Dónde encaja:** ideal para **rutas/senderismo sin cobertura** — que es justo cuando más se necesita. El dueño lleva el teléfono, el perro va con el collar; si se aleja del alcance BLE, avisa.

**Coste `[EST]`:** lógica ya existente (RSSI BLE ya se mide para Find Nearby). Solo requiere un **modo "alerta de alejamiento"** con umbral configurable (X metros) + notificación local en el teléfono (no necesita servidor). Desarrollo bajo.

**Limitaciones (por qué no es un "tracker sin internet" completo):**
- Alcance limitado a ~100 m (no sirve si el perro se pierde a 1 km).
- Requiere que el teléfono esté encendido, con BLE activo y dentro del alcance.
- No sustituye al GPS/LTE: es un **complemento de seguridad para rutas**.

**Veredicto final (2026-08-14):** ❌ **DESCARTADA.** El análisis concluye que no merece la pena: la señal RSSI varía mucho con obstáculos (arbustos, esquinas, el cuerpo del perro) → **avisos falsos** que dañan la confianza; requiere conexión continua (teléfono encendido, BLE activo, perro dentro de ~100 m); y consume batería del collar (el recurso más valioso). Una señal perdida no distingue "a 80 m" de "a 3 km". El GPS/LTE ya cubre el caso real de pérdida. Se documenta aquí como **idea evaluada y descartada** — no se implementa ni se promete.
