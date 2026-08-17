# ARES v4.0 — Estrategia de Contenido, Comunidad y Monetización Temprana
**Versión:** 1.0 | **Motivo:** el usuario identificó una pieza de negocio que no estaba documentada todavía — usar contenido de nutrición/salud canina (apoyado en datos ya existentes en `knowledge_base/`) para atraer audiencia y generar comunidad **antes** de tener el producto físico listo, como palanca de pre-venta/financiación y como canal de monetización temprana independiente del hardware.

---

## 1) Por qué esto es una pieza de negocio real, no solo marketing

ARES ya tiene un activo que no se está explotando: una base de conocimiento estructurada de nutrición y condición corporal canina (`docs/knowledge_base/base_de_conocimiento_canina_mvp_gps_nutricion_ejercicio_v_0.md`, `IMC_por_raza__seed_v1_.csv` con 160 razas, `bmi_simple_bands_v1.csv`). Esto permite ofrecer valor real (saber si el perro está en su peso ideal, cuánto ejercicio necesita según su raza/edad) **sin necesitar el hardware todavía**. Es coherente con el ICP ya definido (`01_PRODUCTO_Y_NEGOCIO.md` §1.5): salud/bienestar general del perro como eje principal.

**El problema que resuelve:** lanzar un hardware nuevo sin audiencia previa es arriesgado (coste de adquisición de cliente alto, cero validación de demanda). Con una web de contenido + herramienta gratuita, se puede: (a) validar que hay interés real antes de fabricar a escala, (b) construir una lista de correos/preventa que sirva como argumento de financiación (ronda, crowdfunding, o simplemente reducir riesgo de las primeras 100-1000 unidades), y (c) generar ingresos tempranos independientes del hardware (afiliación, contenido premium, comunidad de pago).

## 2) A quién se dirige el contenido (dos audiencias distintas, no una)

El usuario lo describe bien: no es "todo el mundo interesado en el producto", son públicos con intereses específicos:

1. **Dueños primerizos / gente que se inicia con perros:** quieren saber lo básico — dónde llevar al perro a socializar, si la comida que le dan es buena, cómo saber si tiene sobrepeso. Contenido tipo guía práctica.
2. **Dueños que ya cocinan o quieren cocinar para su perro:** interesados en recetas caseras seguras, qué alimentos evitar (ya hay una lista de tóxicos estructurada en la base de conocimiento), raciones por peso/raza.
3. **Dueños preocupados por la condición física del perro:** quieren saber si su perro está en su peso ideal, cuánto ejercicio necesita — este es el gancho más fuerte porque ya hay una herramienta calculable (ver sección 4).

**No se dirige (todavía) a:** el público "deportivo"/tracking puro — eso es secundario según el ICP ya decidido, y no tiene un gancho de contenido tan fuerte como la salud/nutrición.

## 3) Mapeo del sistema completo — qué existe y qué falta por fase

| Fase | Qué existe hoy | Qué falta |
|---|---|---|
| **Extracción/generación de contenido** | Base de conocimiento de nutrición (RER/DER, BCS, alimentos tóxicos), CSV de IMC por 160 razas | Ningún canal de publicación todavía (no hay blog, redes sociales, ni newsletter activa) |
| **Captura de audiencia (lead-gen)** | Nada — no hay web pública más allá de `landing/index.html`, que ya está orientada a venta del producto, no a contenido | Falta una web de contenido/herramienta separada (o sección nueva en la landing), formulario de captura de email, política de privacidad/GDPR para ese formulario |
| **Conversión a comunidad** | Nada | Falta decidir canal (newsletter, grupo de Discord/Telegram, Instagram/TikTok) y cadencia de publicación |
| **Monetización temprana (pre-producto)** | Nada | Falta decidir: ¿contenido premium de pago? ¿afiliación con tiendas de pienso/accesorios? ¿solo lista de espera gratuita como preparación de preventa? |
| **Preventa/financiación** | Ya existe un roadmap de preventa de 5 unidades (Mes 1) en `01_PRODUCTO_Y_NEGOCIO.md` §3.3, pero está pensado para venderse a un grupo de WhatsApp de deportistas, no a una audiencia de contenido más amplia | Falta conectar la lista de espera de contenido con esa preventa — hoy son dos flujos desconectados en la documentación |
| **Producto (hardware)** | Documentado extensamente (ver resto de specs) | Sigue pendiente de fabricación física (RR-001 y RR-005 del Risk Register) |

**Conclusión del mapeo:** la fase de contenido/comunidad es la que tiene el gap más grande — hay materia prima (conocimiento) pero cero infraestructura de publicación o captura. Es también la fase más barata y rápida de empezar, porque no depende del hardware ni de decisiones de fabricación.

## 4) La calculadora de peso ideal/IMC — primera pieza de contenido descargable

### 4.1 Qué datos ya existen para construirla
- `docs/combers/IMC_por_raza__seed_v1_.csv`: **160 razas únicas**, con sexo (F/M/U), rango de altura (cm), rango de peso (kg), categoría de tamaño (toy/small/medium/large/giant), y un IMC de referencia con bandas: `imc_normal_min`, `imc_normal_max`, `imc_overweight_start`, `imc_obesity_start`.
- `docs/combers/bmi_simple_bands_v1.csv`: **172 filas**, bandas simplificadas por categoría de tamaño (ej. "giant_general", "large_general"), con ajuste específico para cachorros (`puppy_adj_min/max`) y nota para perros senior.
- `docs/knowledge_base/base_de_conocimiento_canina_mvp_gps_nutricion_ejercicio_v_0.md` §C: reglas de negocio ya definidas — si BCS ≥7, activar "modo adelgazamiento"; si BCS ≤3, alertar y recomendar vet.

### 4.2 Especificación funcional de la calculadora (v1, sin login, gratuita)

**Inputs del usuario:**
1. Raza (selector con las 160 razas del CSV, con opción "Mestizo/No sé" que cae a la categoría `bmi_simple_bands` por tamaño aproximado).
2. Sexo (F/M/No sé → usa fila "U" si existe para esa raza).
3. Peso actual (kg).
4. Altura a la cruz (cm) — **necesaria para calcular el IMC real** (`IMC = peso_kg / altura_m²`), no solo para mirar la tabla.
5. Edad aproximada (para aplicar el ajuste de cachorro si aplica, usando `puppy_adj_min/max` del segundo CSV).

**Lógica de cálculo:**
1. Si la raza está en `IMC_por_raza__seed_v1_.csv`: calcular `IMC = peso / altura²` y comparar contra `imc_normal_min/max`, `imc_overweight_start`, `imc_obesity_start` de esa raza+sexo específicos.
2. Si la raza no está en ese CSV (o el usuario elige "mestizo"): usar `bmi_simple_bands_v1.csv` por categoría de tamaño aproximada (a partir de peso/altura estimados, mapear a toy/small/medium/large/giant).
3. Si es cachorro (edad <12 meses aprox., a definir umbral exacto con un vet o la propia base de conocimiento): aplicar `puppy_adj_min/max` en vez de las bandas de adulto.
4. Devolver una de 4 categorías: **Bajo peso / Ideal / Sobrepeso / Obesidad** — replicando el lenguaje BCS ya definido en la base de conocimiento (BCS ≤3 = alerta+vet, BCS ≥7 = modo adelgazamiento).

**Output al usuario:**
- Resultado visual simple (ej. semáforo o escala) con la categoría.
- **Nunca presentarlo como diagnóstico médico** — mismo principio de "estimación, no diagnóstico" ya aplicado a la estimación de FC por IMU (Bloque C de la sesión anterior) y a la nutrición avanzada en `ARES_planes_basico_vs_premium_v1.md` §2.3.
- Recomendación genérica de siguiente paso (ej. "tu perro está en su peso ideal, mantén su rutina actual" / "tu perro tiene sobrepeso, consulta con tu veterinario sobre un plan de ajuste") — sin prescribir un plan de dieta exacto en la versión gratuita (eso ya está reservado como feature de pago en el Plan Premium, no hay que regalarlo aquí).
- **Gancho de captura de lead:** al final del resultado, ofrecer "recibe seguimiento de la condición de tu perro" o "entérate cuando ARES esté disponible" con un campo de email — este es el punto de conversión de visitante anónimo a lead.

### 4.3 Qué NO incluir en la v1 (para no regalar el valor de pago)
- Cálculo de calorías/DER exacto y plan de alimentación detallado (eso ya es la feature "Dog Fuel Avanzado" de pago, `ARES_planes_basico_vs_premium_v1.md` §2.3) — la calculadora gratuita solo da la categoría de peso, no el plan de corrección.
- Sin tracking de datos del perro a lo largo del tiempo (eso requiere cuenta de usuario y ya es una función del producto/app real).

## 5) Canales y tipo de contenido (por audiencia)

| Audiencia | Formato de contenido | Canal sugerido |
|---|---|---|
| Dueños primerizos | Guías cortas ("qué necesita saber un dueño novato", listas de sitios pet-friendly por ciudad) | Blog/web + Instagram/TikTok (formato visual, fácil de compartir) |
| Dueños que cocinan para su perro | Recetas caseras seguras, lista de alimentos prohibidos con explicación (ya existe la lista completa en la base de conocimiento §A.4) | Blog + Pinterest/Instagram (contenido muy visual, "recetario") |
| Preocupados por condición física | La calculadora de peso ideal (sección 4) como pieza central, artículos de apoyo sobre ejercicio por raza (ya hay datos en `NivelActividad` de la base de conocimiento) | Web (calculadora) + SEO (búsquedas tipo "mi perro está gordo", "peso ideal [raza]") |

**Recomendación de prioridad de canal:** empezar por **web + SEO** (la calculadora es un imán de búsqueda orgánica muy fuerte — "calculadora peso ideal perro [raza]" es un tipo de búsqueda con intención real) antes que redes sociales, que requieren más esfuerzo de producción de contenido continuo. La calculadora puede funcionar como pieza única que genera tráfico recurrente sin publicar contenido nuevo cada semana.

## 6) Monetización temprana — opciones a decidir

1. **Lista de espera gratuita (mínimo viable):** captura de email a cambio de "avisamos cuando ARES esté disponible" + resultado de la calculadora. Sin monetización directa, pero construye el activo de preventa/financiación que el usuario mencionó.
2. **Afiliación con tiendas de pienso/accesorios:** la lista de alimentos "permitidos/con moderación/prohibidos" y las recomendaciones de dieta pueden enlazar a productos recomendados con comisión de afiliado — monetización desde el día 1, sin depender del hardware.
3. **Contenido premium de pago (newsletter o comunidad cerrada):** una vez haya audiencia, ofrecer contenido más detallado (planes de dieta completos, seguimiento) de pago — esto empieza a solaparse con el Plan Premium del producto real, hay que decidir si se posiciona como "antesala" del Premium o como producto de contenido independiente.

**Recomendación:** empezar solo con (1) y (2) — son las de menor fricción y no requieren decisiones de producto todavía. Dejar (3) para cuando ya haya una audiencia real que valide que hay apetito de pago por contenido, evitando construir infraestructura de pago antes de tener demanda confirmada.

## 7) Conexión con la preventa ya documentada

El roadmap actual (`01_PRODUCTO_Y_NEGOCIO.md` §3.3, Mes 1: 5 unidades vendidas a un grupo de WhatsApp de deportistas) y esta nueva estrategia de contenido son, hoy, **dos flujos desconectados**. Se recomienda unificarlos: la lista de espera de la calculadora debería ser la fuente de la preventa de las primeras unidades, no un grupo de WhatsApp aparte — esto además valida mejor el ICP de salud/bienestar (en vez de deportistas) para las primeras ventas reales.

## 8) Próximos pasos concretos (para decidir con el usuario, no asumidos aquí)

1. Decidir si la calculadora vive en `landing/index.html` (sección nueva) o en un dominio/subdominio de contenido separado.
2. Decidir la plataforma de captura de email (Mailchimp, ConvertKit, o algo ya usado en el ecosistema).
3. Priorizar: ¿se construye la calculadora primero, o el blog/guías de contenido primero? (Recomendación: calculadora primero, es el imán más fuerte y ya tiene los datos listos).
4. Decidir si el listado de sitios pet-friendly es contenido curado por el equipo o abierto a comunidad desde el principio (ya se dejó esta misma pregunta abierta en `01_PRODUCTO_Y_NEGOCIO.md` §3.8, del bloque de negocio anterior).
