# ARES v4.0 — Validación de Mercado (España)
**Versión:** 2.0 | **Método:** desk-research con datos públicos reales (no encuesta propia) — todo dato duro está citado con fuente; todo supuesto derivado está etiquetado explícitamente como tal, sin presentarse como cifra oficial.

**Cambios en v2.0 respecto a v1.0:** el usuario pidió profundizar mucho más — no basta con "cuánto gastan al año", hay que desglosar ese gasto por partida (¿cuánto va a "tech/gadgets" específicamente?), cuantificar mejor el segmento de comida húmeda/casera, y cruzar con lo que la competencia real factura para dimensionar qué puede soportar el mercado. Esta versión añade: desglose completo de partidas de gasto, datos financieros reales de competidores (Tractive/Kippy/PitPat), y un análisis de qué implica el precio de ARES frente al presupuesto real de la categoría donde encajaría.

---

## 1) Datos duros verificados (fuentes públicas, julio 2026)

| Dato | Cifra | Fuente |
|---|---|---|
| Perros en España | **9,5 millones** (2025) | REIAC/ANFAAC |
| Hogares españoles con perro | **~27%** (1 de cada 4) | Xataka/censo ANFAAC |
| Gasto medio anual por mascota (perro) | **1.260€** (IPMARK, cifra "conservadora") — otras fuentes hasta 1.908€/año (159€/mes) | IPMARK Mascotas 2025 |
| Mercado alimentación perros España 2025 | **1.139 millones €** (+1,1% interanual) | ANFAAC |
| Mercado alimentación húmeda perros España 2025 | **198 millones €** (+15,5% interanual, frente a 171M€ en 2024) | ANFAAC / Animal's Health |
| **Cuota de húmeda sobre alimentación total de perro** | **17,4%** | Cálculo propio: 198M€ / 1.139M€ |
| Mercado europeo de wearables para mascotas | **~1,3 mil millones $**, CAGR 17,3% (2025-2034) | Fortune Business Insights |
| Españoles que creen que la tecnología puede mejorar el bienestar de su mascota | **71% (7 de cada 10)** | Encuesta Samsung/News Samsung ES |

## 2) Desglose real del gasto anual por partida (esto es lo que faltaba en v1.0)

Fuente: IPMARK Mascotas 2025, sobre base de **1.260€/año** por perro:

| Partida | % del gasto | € /año (sobre 1.260€) |
|---|---|---|
| Alimentación | 41% | **~517€** |
| Veterinario | 19% | ~239€ |
| Seguros | 13% | ~164€ |
| Cuidados estéticos | 11% | ~139€ |
| Higiene | 8% | ~101€ |
| **Juguetes y accesorios** | **7%** | **~88€** |

**Hallazgo crítico: no existe un desglose oficial de "tecnología/wearables/GPS" como partida separada.** Todo lo que sería un GPS tracker, collar inteligente o gadget cae dentro de la categoría genérica "Juguetes y accesorios" (7%, ~88€/año) — y esa partida no distingue cuánto de ese gasto es tecnología frente a correas, camas, juguetes tradicionales, etc. **No hay que inventar un porcentaje aquí que no existe.**

### 2.1 Implicación directa para el pricing de ARES (esto cambia el análisis)

El hardware de ARES cuesta **139-159€**. Comparado con el presupuesto anual típico de la partida donde encajaría (accesorios/juguetes, ~88€/año):

> **El precio de ARES equivale a ~1,6 veces todo el presupuesto ANUAL que un dueño medio dedica a accesorios y juguetes.**

**Esto tiene una implicación real que no estaba en la v1.0 del análisis:** ARES no compite por una porción del gasto rutinario de accesorios — es una **decisión de compra extraordinaria**, más parecida en magnitud a un gasto veterinario puntual (~239€/año) que a un accesorio más. Esto:
- Confirma por qué **todos los competidores analizados vendieron con financiación/pago fraccionado o packs con descuento** (Weenect "pack XS con 1 año incluido", planes de 2-3-5 años con descuento) — es una estrategia necesaria para hacer digerible un gasto que excede el presupuesto anual normal de esa categoría, no un simple "extra opcional".
- Sugiere que el marketing debe posicionar ARES como inversión en **salud y seguridad** (categorías con mayor presupuesto: veterinario 19%+seguros 13% = 32% del gasto total, muy por encima del 7% de accesorios) en vez de como "gadget/accesorio" — coherente con el ICP ya decidido (salud/bienestar, no "gadget deportivo").
- Refuerza que el Plan Esencial de suscripción (5€/mes = 60€/año, ya decidido en la sesión anterior) es relativamente pequeño comparado con el gasto veterinario (239€/año) — la suscripción no es el obstáculo de pricing, el desembolso inicial del hardware sí lo es.

## 3) ¿Cuánta gente compra húmeda, y cuántos de esos cocinan en casa?

- **Húmeda: 17,4% de cuota de gasto en alimentación de perro** (198M€ de 1.139M€), dato duro ya confirmado en v1.0, **creciendo +15,5%/año** frente al +1,1% del mercado general.
- **Casera/BARF: sigue sin existir un dato oficial de cuota de mercado o porcentaje de perros.** Se revisó de nuevo específicamente el "2º Barómetro de Hábitos y Tendencias de los Pet Parents en España y Portugal 2025" (AEDPAC + Hamilton Global, encuesta a 709 personas responsables de mascotas en España) — este estudio sí confirma gasto medio en comida (66€/mes en perro, alineado con el 41% de partida de alimentación) pero **tampoco desglosa cuánta gente cocina en casa frente a compra pienso/húmeda comercial.** No hay que inventar esta cifra — se mantiene como hueco de dato real, tal como en v1.0.
- **Lo que SÍ se puede decir con solidez:** el crecimiento del +15,5%/año en húmeda es una señal de migración de gasto hacia "mejor calidad percibida" que es coherente con (aunque no prueba directamente) un interés creciente por dietas más naturales/caseras — pero el barómetro solo mide gasto en producto comercial, no captura el segmento que cocina 100% en casa sin comprar producto de marca (que por definición no aparece en cifras de "mercado de alimentación").

## 4) Qué puede soportar el mercado — comparando contra competidores reales (esto faltaba en v1.0)

Datos financieros reales de competidores, para dimensionar qué tamaño de negocio es realista:

| Competidor | Facturación/ARR real | Usuarios activos | Nota |
|---|---|---|---|
| **Tractive** | **~100 millones € de ARR** (2024-2025), +35-40% crecimiento esperado 2025 | **1,4 millones** de usuarios activos en 175 países | Adquirida por Bending Spoons (marzo 2026) — el líder claro del sector, referencia de "techo" de mercado |
| **Kippy** | **~$770K/año** (2025), equipo de 7 personas | No público | Empresa pequeña — referencia de "suelo" viable: un negocio rentable de nicho puede sostenerse con una fracción mínima del mercado |
| **PitPat** | Ha levantado $19,3M en financiación total, 45 empleados | No público | Empresa mediana, tamaño intermedio entre Kippy y Tractive |

**Lo que esto dice sobre "cuánto puede soportar el mercado":**
- El rango de negocios viables va desde **~$770K/año (Kippy, empresa pequeña rentable)** hasta **~100M€/año (Tractive, líder de categoría)** — es un mercado con espacio real para jugadores de tamaños muy distintos, no solo para "el ganador se lo lleva todo".
- Tractive por sí solo (1,4M usuarios) ya captura una fracción muy pequeña del TAM europeo de perros (decenas de millones) — confirma que el mercado está lejos de saturado, incluso el líder tiene mucho margen de crecimiento (de ahí su +35-40% de crecimiento esperado).
- El roadmap de ARES (SOM: 5.000 unidades en 12 meses) es una fracción diminuta incluso comparado con Kippy (empresa "pequeña" del sector) — es un objetivo alcanzable sin necesitar capturar cuota de mercado significativa frente a nadie.

## 5) TAM / SAM / SOM — actualizado con el nuevo desglose

- **TAM:** 9,5 millones de perros en España — dato duro.
- **SAM:** se mantiene el supuesto razonado de v1.0 (~15% de dueños dispuestos a invertir en tech/salud premium, apoyado en la cuota de húmeda) → **~1,4 millones de perros**. **Matiz nuevo de v2.0:** dado que el precio de ARES excede el presupuesto anual normal de "accesorios" (sección 2.1), el SAM real de compradores dispuestos a hacer ese desembolso extraordinario es probablemente **menor** que ese 15% — sin dato para afinarlo más, se mantiene como rango, no cifra puntual.
- **SOM:** 5.000 unidades (roadmap ya documentado) — con el nuevo contexto de sección 4 (comparado con Kippy, Tractive), sigue siendo un objetivo modesto y alcanzable, no ambicioso en exceso.

## 6) Perfil del comprador y miedos — sin cambios sustanciales frente a v1.0

Se mantiene el análisis de v1.0 (secciones 5-6 de esa versión): hipótesis razonada sobre perfil de vivienda/uso (jardín/finca/campo vs piso) sin dato oficial, y los miedos ya documentados del informe competitivo (pérdida del perro, desconfianza en batería, fatiga de suscripciones, preocupación por peso/nutrición).

## 7) Conclusión actualizada

**Sigue siendo un mercado viable**, pero con una corrección importante de v1.0 a v2.0: **el obstáculo real no es "si hay presupuesto en el mercado" (sí lo hay, y de sobra — el mercado mueve miles de millones), sino que ARES compite por un tipo de gasto extraordinario/puntual, no por gasto rutinario.** Esto refuerza (no contradice) las decisiones ya tomadas:
- El posicionamiento en salud/bienestar (no "gadget") es la estrategia correcta, porque esas categorías (veterinario+seguros = 32% del gasto) tienen presupuesto mucho mayor que "accesorios" (7%).
- Facilitar el desembolso inicial (financiación, packs, o el modelo tipo PitPat/Weenect de "pack con año incluido") es más relevante de lo que se había valorado — es una palanca de conversión, no solo un detalle de checkout.
- El mercado tiene espacio de sobra (comparado con la escala de Tractive/Kippy/PitPat) para que el SOM de 5.000 unidades sea perfectamente alcanzable sin depender de arrebatar cuota a nadie.

**Sigue habiendo huecos de dato reales (no inventados):** porcentaje exacto de gente que cocina en casa para su perro, y desglose específico de cuánto del 7% de "accesorios" es tecnología. Estos dos huecos no tienen fuente pública — se mantienen como limitación explícita del análisis, a validar con datos propios de la web cuando esté en marcha.
