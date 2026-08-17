# 01_PRODUCTO_Y_NEGOCIO.md
**Versión:** 4.0 | **Estado:** Final | **Audiencia:** Marketing, Ventas, Inversores, Gestión

---
## 1. Propósito de este Documento
*Este documento consolida la **visión de producto, la arquitectura de alto nivel y la estrategia de negocio** de ARES v4.0. Sirve como guía maestra para entender el producto, su mercado y su plan de comercialización.*

---
## 1.5. Posicionamiento y Perfil de Cliente (ICP) — v4.0

*Decisión del usuario, sesión de cierre de brechas competitivas y de negocio.*

### 1.5.1. Eje principal: salud y bienestar general del perro
ARES **no** lidera con "tracker deportivo". El eje principal es ayudar al dueño a saber si su perro **está bien**: si come lo que le corresponde, si hace el ejercicio adecuado para su raza/edad/complexión, si descansa lo necesario. Esto conecta directamente con el trabajo ya existente en `docs/knowledge_base/base_de_conocimiento_canina_mvp_gps_nutricion_ejercicio_v_0.md` (fórmulas RER/DER, niveles de actividad por tamaño/raza, BCS/IMC) e `IMC_por_raza__seed_v1_.csv` — **este es el activo diferencial real** que sostiene el mensaje de salud, no una promesa vacía de marketing.

**Caso de uso central:** detectar cuándo un perro hace **menos** ejercicio del recomendado para su perfil (sedentarismo, riesgo de sobrepeso) o, en el otro extremo, cuando hace **más** actividad de la que su condición física recomienda (sobreesfuerzo) — y ajustar automáticamente la recomendación de nutrición y ejercicio a la condición física actual del animal (no genérica, sino calibrada por raza/edad/BCS).

### 1.5.2. Eje secundario: perros muy activos / de trabajo (extrapolación, no el mensaje principal)
El mismo motor de datos (actividad real medida por IMU, gasto calórico, comparación con el nivel esperado para su perfil) sirve igual de bien para un perro con mucha actividad física — simplemente con umbrales de referencia más altos ("Alta" en `NivelActividad`: 90-150 min/día, 6-12km). **No se lidera con este ángulo** porque el usuario lo considera "muy nicho" si se pone por delante — se ofrece como una extensión natural del mismo sistema, útil para el segmento de dueños con perros de trabajo/muy activos, pero secundario en el mensaje de marca.

### 1.5.3. Eje adicional: social y descubrimiento para dueños nuevos
Ayudar a socializar al perro y facilitar la vida a dueños primerizos: directorio de sitios pet-friendly (bares, restaurantes que admiten perros), zonas de juego/"pipicans", tips básicos para quien se estrena en el mundo de las mascotas. Ningún competidor analizado en `docs/Análisis Competitivo de Localizadores GPS para Perros (Europa).md` cubre esto de forma explícita — es un diferenciador adicional, de menor prioridad que la salud pero coherente con la misma idea de "hacerlo fácil" para el dueño.

### 1.5.4. Orden de prioridad del proyecto (confirmado por el usuario)
1. **Dispositivo** — hardware, diseño físico, marca (base del producto).
2. **Modelo de negocio** — pricing, tiers, sostenibilidad económica.
3. **Funcionalidades y extras** (incluida la web/app) que aportan valor y son monetizables — construidas sobre la base ya sólida, no antes.

---
## 2. Arquitectura de Producto (ARES v4.0)

*Extraído de `Diseño orientativo.txt`*

### 2.1. ALCANCE: ENFOQUE EN MEDIUM Y LARGE
*   Esta especificación se centra en los modelos **Medium (~2750 mAh)** y **Large (~4000 mAh)**.
*   El modelo **Small/Nano queda postpuesto** para una futura fase, con un diseño simplificado.

### 2.2. MÓDULO CHIP ARES v4.0 (ÚNICO PARA TODOS)
Este es el cerebro del dispositivo, unificado para garantizar la máxima calidad y rendimiento.
```
**MÓDULO CHIP 37x28mm | IP68**
┌──────────────────────────┐
│ LilyGo T-SIM7000G S3     │ ← **GNSS+LTE Cat-M1 mundial**
│ Bosch BMI270             │ ← **Antifraude 99.5%**
│ Ignion A101 + LNA        │ ← **Precisión objetivo <1m (pend. validar campo)**
│ Conectividad 1NCE        │ ← **Nano-SIM (prototipo), MFF2 soldada (venta)**
│ 12x LEDs SMD 1206        │ ← **Sistema de Luces v4**
└──────────RAIL POGO───────┘
```
*   **Calidad Consistente:** Los modelos Medium y Large comparten el mismo chip, garantizando idéntico rendimiento.

### 2.3. GAMA DE MÓDULOS DE BATERÍA ("POWER PACKS")
La diferenciación entre modelos se basa en el "Power Pack". Ambos usan una carcasa con la misma huella interna de **36x58mm**, variando solo en el grosor.

| **Modelo** | **Capacidad** | **Peso Total*** | **Uso Ideal** |
|------------|---------------|-----------------|-------------------|
| **Medium** | **~2750mAh** | **~64g** | Perros Medianos/Grandes |
| **Large** | **~4000mAh** | **~67g** | Uso Extensivo / Perros XL |

*\*Peso total estimado = Módulo Chip (~44g) + Módulo Batería + Batería.*

```
**MÓDULO BATERÍA CON CARGA MAGNÉTICA:**
┌──────────────────────────┐
│ BQ24040 TI (Carga Segura)│ ← **32°C seguridad térmica**
│ Conector Magnético IP68  │ ← **Carga externa sin puertos**
│ LiPo (2750 o 4000mAh)    │
└──────────RAIL POGO───────┘
```

### 2.4. VEREDICTO FINAL: ARQUITECTURA v4.0
```
[OK]  **ARQUITECTURA MODULAR VALIDADA:**
1. **UN Módulo Chip** para consistencia de calidad.
2. **DOS Módulos de Batería** para el lanzamiento (Medium, Large).
3. **UNA Carga Magnética** para máxima comodidad e impermeabilización.
4. **UN Sistema de Luces v4** robusto y sin sensores.
```

---
## 3. Estrategia de Negocio y Comercialización

*Extraído de `MARkETING.txt`*

### 3.1. ESTADO LEGAL COMERCIALIZACIÓN ESPAÑA 2026
*   **FASE 1-2 (Prototipo y Pre-order):** Legalmente viable bajo "edición limitada" con módulos pre-certificados.
*   **FASE 3 (Producción en masa):** Requiere inversión en certificaciones (RED, ROHS, EMC) estimada en **~4.800€**.

### 3.2. ESTRATEGIAS DE MONETIZACIÓN
| **Modelo** | **Precio** | **Margen Bruto** | **Notas** |
|------------|------------|------------------|-----------|
| **Hardware** | **120-149€** | **~87-122%** | Basado en coste de ~65€ (PVP v2.0, 2026-08-14) |
| **Suscripción App** | **Esencial 6€/mes · Básico 10€/mes · Premium 12,99€/mes** (v2.1, 2026-08-14) | **~43-48% neto a escala** (tras costes de servicio e impuestos) | Ver `ARES_planes_basico_vs_premium_v1.md` — **no existe plan 100% gratuito**: la conectividad celular (SIM + red) tiene un coste real que siempre se traslada, aunque sea mínimo, al plan de entrada. Costes de servicio detallados en `ARES_Escalabilidad_Precios_Margenes.md` §4.2 |um_v1.md` — **no existe plan 100% gratuito**: la conectividad celular (SIM + red) tiene un coste real que siempre se traslada, aunque sea mínimo, al plan de entrada |

**RECOMENDADO:** Venta de hardware con un margen saludable + modelo de suscripción (sin tier gratuito real) para cubrir el coste de conectividad y financiar los tiers de valor añadido (Básico/Premium).

**Nota de reconciliación (higiene documental):** esta tabla usaba antes "Freemium App | 0€ + 4.99€/mes", en contradicción directa con el principio "No hay plan gratis" de `ARES_planes_basico_vs_premium_v1.md`. Se corrige aquí para que ambos documentos coincidan: el plan de entrada existe, tiene un coste mínimo ligado al coste real de datos (~1,25€/mes, ver Bloque de análisis de red), y no se presenta como "0€".

### 3.3. HOJA DE RUTA COMERCIAL (6 MESES)
*   **MES 1: PROTOTIPO + PRE-VENTA (5 unidades):** Validar producto y conseguir primeros ingresos.
*   **MES 2: APP FLUTTER + EMQX (50 unidades):** Desarrollar App y escalar preventa.
*   **MES 3: CERTIFICACIÓN CE (100 unidades):** Iniciar trámites para venta masiva.
*   **MES 6: ESCALA INDUSTRIAL (1000+ unidades):** Reducir coste a ~45€/u y vender en Amazon FBA.

### 3.4. PROYECCIONES FINANCIERAS
*Basado en un coste unitario promedio de 65€ y un PVP promedio de 134,5€ (media 120/149, PVP v2.0 2026-08-14).*

| **Mes** | **Unidades** | **Ingresos** | **Coste** | **Ganancia** | **Acumulado** |
|---------|--------------|--------------|-----------|--------------|---------------|
| **1** | 5u | 672€ | 325€ | **+347€** | **347€** |
| **2** | 50u | 6.725€ | 3.250€ | **+3.475€** | **3.822€** |
| **3** | 100u | 13.450€ | 6.500€ | **+6.950€** | **10.772€** |
| **6** | 1.000u | 134.500€| 45.000€ | **+89.500€**| **100.272€**|
| **12**| 5.000u | 672.500€| 225.000€| **+447.500€**| **547.772€**|

*Nota: cifras actualizadas con los PVP v2.0 (120€ Medium / 149€ Large, media 134,5€). Sin impuestos (ver `ARES_Escalabilidad_Precios_Margenes.md` §3).*

### 3.5. PAQUETES DE HARDWARE
| **Paquete** | **Hardware** | **App** | **PVP** | **Coste Total Est.** | **Margen** |
|-------------|--------------|---------|---------|--------------------|------------|
| **ARES Medium** | Tracker 2750mAh | Plan Esencial | **120€** | ~64€ | **~56€ (87%)** |
| **ARES Large** | Tracker 4000mAh | Plata 12m| **149€**| ~67€ | **~82€ (122%)**|
| **FAMILY PACK** | 2× Medium (o combo mixto) | Oro 12m | **desde 199€** | ~128€ (2× M) | **~71€ (36%)** |

*Nota: precios PVP v2.0 (2026-08-14), redondeados hacia arriba sobre el suelo viable de ~117€ (Medium). El margen mostrado es bruto, antes de impuestos (ver `ARES_Escalabilidad_Precios_Margenes.md` §3).*

### 3.6. ANTI-FRAUDE GPS: DETECTAR COCHE vs CAMINATA REAL
*   **Tecnología:** **Bosch BMI270** + Sensores del Teléfono.
*   **Ventaja Comercial:** Asegura la integridad de los datos de actividad, una característica premium para deportistas y competiciones.

### 3.7. Plan Esencial (tier de entrada) — diseño basado en coste real de conectividad

**Contexto:** el coste de conectividad celular (SIM + red) es un suelo real que no puede bajar a cero — verificado en vivo (julio 2026) que **1NCE High Data sigue vigente**: 5€/GB + 12€ alta única, sin cuota fija mensual, pago por uso puro (ver `ARES_Analisis_Red_y_Consumo_v1.md`). El modelo de consumo de datos de ese mismo documento muestra que un patrón de uso típico (8h reposo + 2h paseo/día) consume **~1,4 MB/mes**, muy por debajo de los 250MB/mes de referencia — el coste real de datos por dispositivo es de aproximadamente **1,25-2€/mes**, con margen amplio incluso si el consumo real es varias veces mayor al estimado.

**Dos opciones de estructura de precio para el Plan Esencial, ambas viables con estos números:**

| Opción | Cómo funciona | Ventaja | Riesgo |
|---|---|---|---|
| **A) Suscripción mínima mensual** | Se traslada el coste de datos (~1,25-2€/mes) + margen pequeño como cuota mensual visible, ej. ~2,99€/mes | Simple de operar, alineado con cómo funciona el resto del mercado (Tractive, Weenect, Kippy) | El usuario sigue viendo "otra suscripción más" — no ataca la objeción de fatiga de suscripciones que sí resuelve PitPat |
| **B) Coste de conectividad pre-pagado en el hardware** | El PVP del hardware incluye conectividad por un periodo definido (ej. 1-2 años) sin cuota mensual visible para el Plan Esencial | Se siente como "sin suscripción" en el tier de entrada — contrarresta directamente la objeción de PitPat; fuerte para marketing | Requiere provisionar el coste de datos por adelantado en el PVP (impacto pequeño dado el coste real ~1,25-2€/mes, pero hay que sumarlo al cálculo de margen de `01_PRODUCTO_Y_NEGOCIO.md` §3.5); requiere decidir qué pasa al vencer el periodo pre-pagado (renovación obligatoria vs degradación a "solo alertas")|

**Recomendación para decidir en la siguiente iteración de precios:** dado que el coste real de datos es bajo (~1,25-2€/mes) comparado con el PVP del hardware (139-159€), la Opción B es económicamente viable — pre-pagar 1 año de conectividad Esencial cuesta ~15-24€, una fracción pequeña del margen ya existente (~75-92€ por unidad). Esto convertiría el mensaje de venta en "localización incluida, sin sorpresas" — más parecido a PitPat que a Tractive — sin perder los tiers de pago (Básico/Premium, ya definidos en `ARES_planes_basico_vs_premium_v1.md`) como los que realmente generan ingreso recurrente vía funciones de valor añadido (compartir ubicación avanzado, salud/nutrición avanzada, historial extendido, social).

**Estos tiers superiores no se tocan** — la Opción B solo afecta al tier de entrada, no canibaliza el valor de Básico/Premium porque estos siguen ofreciendo funciones que el Plan Esencial no incluye.

### 3.8. Capa social/descubrimiento pet-friendly (nueva pieza de producto)

Directorio de sitios que admiten perros (bares, restaurantes, alojamientos), zonas de juego/"pipicans" y tips de socialización para dueños primerizos. Dos enfoques posibles, a decidir cuando se llegue a esta fase (prioridad 3 según §1.5.4, después de dispositivo y negocio):
- **Contenido curado editorialmente:** ARES mantiene una base de datos inicial (empezando por ciudades/zonas principales), más controlable en calidad pero requiere mantenimiento continuo.
- **Generado por comunidad:** los propios usuarios marcan y valoran sitios, escala mejor pero requiere moderación básica desde el lanzamiento (evitar spam/información falsa).
- **Recomendación:** empezar curado (barato de validar con pocos usuarios iniciales) y abrir a comunidad cuando haya masa crítica de usuarios activos — patrón estándar para evitar un directorio vacío en el lanzamiento.

### 3.9. Garantía extendida y devoluciones (evaluación pendiente)

Weenect ofrece garantía de por vida; PitPat, devolución de 42 días sin preguntas. ARES, como producto nuevo sin historial de marca, se beneficiaría de una política de confianza similar. **Pendiente de decisión económica** (impacto en RMA/soporte) antes de comprometerlo en marketing — no se fija aquí una política concreta, se deja como acción de seguimiento para cuando el Bloque de negocio (prioridad 2) se cierre con cifras de coste de soporte/devolución.

### 3.10. Modo "estación WiFi en casa" (evaluación, no comprometido)

Fi y Weenect ofrecen un modo de bajísimo consumo cuando el perro está en casa, vía estación base WiFi. ARES ya usa WiFi para detección de "zona segura" (apaga GNSS/LTE, ver `02_ESPECIFICACION_TECNICA.md` §2.4) — el mismo mecanismo, sin hardware adicional. **No se requiere una estación base dedicada nueva**: basta con que el marketing comunique esta función existente con el mismo lenguaje que la competencia ("modo hogar de bajo consumo"), en vez de dejarla como un detalle técnico interno sin visibilidad comercial.

### 3.11. Decision Log (Bloque de Negocio, sesión de cierre de brechas)

- **DL-001**: ICP principal = salud/bienestar general del perro (nutrición+ejercicio+descanso ajustados a raza/edad/BCS), no "perro deportivo". Motivo: el ángulo deportivo se considera muy nicho como mensaje principal; el activo diferencial real es el trabajo ya hecho de IMC/BCS por raza. Afecta: `funciones.txt`, `MARkETING.txt`, landing (pendiente de propagar redacción final a landing/marketing en una siguiente pasada de copy).
- **DL-002**: El ángulo "perro muy activo/deportivo" se mantiene como extrapolación secundaria del mismo motor de datos, no como propuesta de valor principal. Rompe si: se vuelve a liderar marketing con "deportivo" sin pasar por esta decisión.
- **DL-003**: No existe plan 100% gratuito — se corrige la tabla "Freemium 0€" a "Plan Esencial de bajo coste", alineado con el principio ya existente en `ARES_planes_basico_vs_premium_v1.md`. Motivo: coste real de conectividad celular (1NCE ~1,25-2€/mes) no puede ser cero.
- **DL-004**: Precio de hardware unificado a 139-159€ (Medium/Large), eliminando la cifra "129€" que solo aparecía en `01_PRODUCTO_Y_NEGOCIO`. **Actualizado 2026-08-14 a 120-149€ (PVP v2.0)** — ver `ARES_Escalabilidad_Precios_Margenes.md`..md` y contradecía `MARkETING.txt`. Rompe si: se reintroduce 129€ sin actualizar ambos documentos a la vez.
- **DL-005**: Pendiente de decisión (no cerrada en esta sesión): si el Plan Esencial se cobra como suscripción mínima visible (Opción A, §3.7) o se pre-paga en el precio del hardware (Opción B, §3.7). Requiere modelar el impacto en margen antes de comprometer una de las dos en marketing.
- **DL-006**: Capa social/descubrimiento pet-friendly aprobada como pieza de producto futura (prioridad 3, después de dispositivo y negocio) — enfoque recomendado: curado primero, comunidad después.
- **DL-007**: Garantía extendida/devolución y "modo estación WiFi en casa" quedan como evaluación pendiente, no como compromiso de producto — no publicitar hasta decisión explícita.
- **DL-008 (cierra DL-005/RR-007):** Plan Esencial fijado en **5€/mes**, sin subir el precio del hardware (se mantiene 120-149€ desde 2026-08-14, antes 139-159€). A este precio el margen neto (tras 35% de carga fiscal aplicada por el usuario) es de ~2,75-3,24€/mes/cliente incluso en el escenario de consumo x10 (el más exigente considerado realista) — ver `ARES_Analisis_Red_y_Consumo_v1.md` §5.4 y §8 para el detalle completo de escenarios y márgenes. Motivo: el usuario prefirió fijar un suelo de suscripción más alto que el mínimo viable (2,99€) para tener colchón de margen, en vez de explorar la Opción B (prepago en hardware). **Actualizado 2026-08-14 (v2.1): Esencial fijado en 6€/mes** al incorporar los costes de servicio reales (nube, pasarela, soporte, amortización) que a 5€ dejaban el margen de arranque en ~27% — ver `ARES_Escalabilidad_Precios_Margenes.md` §4.2-4.3.
- **DL-009:** Verificado el contrato legal real de 1NCE (no solo su web de marketing): permanencia de 12 meses por SIM con renovación automática si no se cancela con 2 meses de preaviso; subida de precio solo permitida tras 12 meses de contrato activo, máx. 1 vez/año, con 1 mes de aviso, y solo si hay aumento real de costes de 1NCE. Esto se incorpora como riesgo gestionable (no crítico) en el Risk Register (`RR-007` actualizado).
- **DL-010:** Comparado el precio de hardware de ARES (120-149€ desde 2026-08-14, antes 139-159€) contra el rango real de competencia: sigue por encima del precio puro de los líderes (Tractive ~50€, Weenect ~32-46€, Kippy ~50€), pero se compite por **salud/nutrición** (diferencial), no por precio. Ver `ARES_Escalabilidad_Precios_Margenes.md`.tive 50-70€, Weenect 45-129€ con pack) — no en la franja baja sin features (Kippy 40€, genéricos 30-50€). No se recomienda bajar a esa franja baja porque implicaría vender por debajo de coste (~64-67€) o recortar features que no son comparables a esos competidores.
- **DL-011:** Revisado el desglose de coste de hardware (BOM): el módulo LilyGo T-SIM7000G S3 es el 49% del coste base (28€ de 57,4€) — mayor palanca de ahorro futura, pero requiere I+D de PCB propio (fuera de alcance de esta sesión, ver `ARES_Risk_Register_v1.md` para nota de seguimiento). La celda LiPo (6,5-9,5€ según SKU) parece ya razonablemente cotizada frente a precios de mercado verificados (celdas 4000mAh genéricas ~4,4-4,8€ a 1000+ uds) — no hay evidencia de sobreprecio ahí, pero falta cotización directa y específica para el formato 123450/2750mAh exacto de ARES.
- **DL-012:** Confirmado con el propio roadmap comercial que a MOQ~100 unidades (fase de certificación CE, Mes 3) el coste de hardware se mantiene en ~65€/unidad, igual que en prototipo — el salto de precio grande a ~45€/unidad solo llega a partir de 1000+ unidades (economía de escala industrial). El margen de hardware en la fase de 100 unidades (74-94€/unidad según SKU) es amplio y no requiere ajuste de pricing.
- **DL-013 (re-verificación de precios de competencia, verificado en vivo):** Weenect ha bajado su hardware de ~€79-129 a ~€32-46; Kippy ha subido de ~€40 a ~€50; Tractive se mantiene similar (~€70-73); **PitPat ha bajado significativamente de ~€260 a ~$159 (~€147)**, manteniendo su modelo sin suscripción. Esto último es relevante: el punto de referencia de precio para un modelo "todo incluido, sin suscripción" ya no es €260 (una franja premium lejana), sino ~€147-160 — muy cerca de donde ya está posicionado ARES (139-159€). Si en el futuro se reconsidera la Opción B (prepago de conectividad en el hardware, ver DL-005/DL-008), este dato hace que sea más competitivamente viable de lo que parecía en el análisis original.
