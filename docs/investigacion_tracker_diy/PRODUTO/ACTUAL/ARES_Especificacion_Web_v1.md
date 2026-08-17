# ARES v4.0 — Especificación de Páginas Web (para diseñador)
**Versión:** 2.0 | **Contexto:** solo existe hoy `landing/index.html` (venta del producto). Este documento especifica en detalle las 3 páginas nuevas ya priorizadas (Calculadora, Pet-Friendly, Landing de captura/preventa) — sección por sección, con contenido, animaciones concretas y tokens de marca ya definidos, listo para maquetar sin tener que volver a preguntar qué va en cada bloque.

**Cambios en v2.0 respecto a v1.0:** el usuario pidió profundizar mucho más el detalle de cada página (bloques de contenido, animaciones, uso de recursos de Pick4Design) para poder entregarlo a un diseñador. Se revisaron los documentos de marca ya existentes (`landing/docs/TONO_DE_VOZ.md`, `ARES_LANDING_CREATIVE_BRIEF.md`) y el arsenal de herramientas de animación ya vendorizadas en Pick4Design (`C:\Users\solde\OneDrive\Desktop\EJECUTER_EXT\Pick4Design\tools\`) para dar recomendaciones concretas, no genéricas.

---

## 0) Base de marca ya definida (fuente de verdad, no repetir, solo aplicar)

Todo lo de abajo ya está decidido en `landing/docs/ARES_LANDING_CREATIVE_BRIEF.md` y `TONO_DE_VOZ.md` — estas 3 páginas nuevas deben ser **consistentes** con esto, no reinventarlo:

- **Paleta "Calma Natural":** gris carbón `#454851` (fondo, 60%), verde salvia `#7BAE7F` (CTAs/acentos, 10%), blanco lila `#FCEFF9` (texto, 30%). Psicología: "naturaleza + precisión".
- **Tipografía:** Badeen Display (H1/H2), Bruno Ace SC (H3/H4/labels), Orbitron (body), JetBrains Mono (datos técnicos).
- **Anti-patrón IA (prohibido):** badges con fondo+bordes redondeados, gradientes arcoíris, border-radius >4-8px, sombras neón, scrollbar nativo visible, iconos placeholder genéricos.
- **Tono de voz:** estructura PAS (Problema→Agitación→Solución) para bloques emocionales; estructura "Qué ganas → Por qué → En tu día a día" para bloques semi-técnicos. Vocabulario permitido vs. prohibido ya tabulado en `TONO_DE_VOZ.md` (nunca decir "BMI270/IMU/ESP32", decir "sensores de actividad").
- **Motores de compra a activar:** Automejora ("mejor dueño"), Curiosidad/Escepticismo ("la mayoría de trackers mienten"), Seguridad/Paz mental (motor principal para estas 3 páginas nuevas, dado que tratan salud/nutrición/localización de sitios seguros).

## 1) Herramientas de animación disponibles (Pick4Design, ya vendorizadas — no hay que instalar nada nuevo)

Revisado `C:\Users\solde\OneDrive\Desktop\EJECUTER_EXT\Pick4Design\tools\`: **no hay una biblioteca de referencias de sitios de mascotas ya extraída** (solo hay una referencia guardada, `originkit-liquid-distortion`, no específica de este sector) — el valor real de Pick4Design aquí son las librerías de animación ya vendorizadas, listas para usar sin depender de CDN externo:

| Herramienta | Qué hace | Dónde aplicarla en estas 3 páginas |
|---|---|---|
| **GSAP** (ya en uso en `landing/index.html`) | Animaciones de timeline, scroll-trigger, texto | Reutilizar el mismo motor ya usado en la landing de venta — coherencia técnica y visual |
| **Lenis** | Scroll suave (smooth scroll) | Aplicar en las 3 páginas nuevas para que el scroll se sienta igual de premium que la landing principal |
| **Splitting.js** | Divide texto en caracteres/palabras para animar letra a letra | Reveal del resultado de la calculadora (ej. la categoría "IDEAL"/"SOBREPESO" apareciendo letra a letra, dramatizando el momento clave de la página) |
| **react-bits / originkit** | Componentes de UI animados ya construidos (cards, botones, texto) | Cards de resultados en la página Pet-Friendly, botones CTA con hover consistente |
| **rough-notation** | Subrayados/marcas "dibujadas a mano" sobre texto | Resaltar cifras clave en la calculadora (ej. rodear el peso ideal calculado) — usar con moderación, contrasta con la estética "militar-quirúrgica" ya definida, solo si encaja con el anti-patrón (revisar antes de usar, puede chocar con "sin decoración")|
| **vanta / shadergradient** | Fondos animados (partículas, gradientes shader) | Fondo del Hero de la página 3 (Landing/Preventa) — mismo recurso que ya se contempla en el brief original para el hero de la landing principal (`hero-bg`) |
| **liquid-glass-js** | Efecto de vidrio líquido/glassmorphism | Uso opcional en overlays de resultado (ej. la tarjeta de resultado de la calculadora) — **verificar contra el anti-patrón** antes de aplicar, puede no encajar con la estética "sin decoración" ya definida |

**Recomendación general:** priorizar GSAP+Lenis (ya en uso, cero fricción de integración) para mantener consistencia técnica exacta con la landing de venta. Usar el resto (rough-notation, liquid-glass-js) solo si el diseñador confirma que encaja con el anti-patrón ya definido — están disponibles, pero no son obligatorios.

---

## 2) Página 1 — Calculadora de Peso Ideal / Condición Física

**Objetivo:** pieza central de captación (imán de SEO + conversión a lead). Motor de compra principal: **Seguridad/Automejora** ("¿estoy siendo buen dueño con su alimentación?").

### Estructura por secciones

| # | Sección | Contenido | Animación sugerida |
|---|---|---|---|
| 1 | **Hero corto** | Headline tipo "¿Sabes si tu perro está en su peso ideal?" (estructura PAS breve, no el PAS largo de la landing de venta — aquí se busca ir directo al formulario). Subhead: "Descúbrelo en menos de un minuto." | Scramble text reveal del headline (mismo efecto ya usado en el Hero de `landing/index.html`, vía GSAP ScrambleTextPlugin) para dar continuidad de marca |
| 2 | **Formulario** | Inputs: raza (selector, 160 opciones del CSV + "Mestizo/No sé"), sexo, peso (kg), altura a la cruz (cm), edad aproximada. Un input a la vez o todos juntos — decisión de UX del diseñador, pero recomendado mostrar progreso (ej. barra fina 2px arriba, coherente con el anti-patrón "scrollbar oculto + barra de progreso") | Transición entre pasos con fade/slide (GSAP), sin gastar presupuesto de animación en el formulario en sí — se reserva el impacto visual para el resultado |
| 3 | **Resultado** | Categoría (Bajo peso/Ideal/Sobrepeso/Obesidad) — lenguaje "estimación, no diagnóstico" (nunca "diagnóstico médico"). Mostrar visualmente como escala/semáforo, no como badge con fondo de color (prohibido por anti-patrón) — usar línea/marcador sobre una escala horizontal | **Momento clave de la página:** reveal del resultado letra a letra con **Splitting.js**, dramatizando el instante en que el usuario ve la categoría de su perro — coherente con el "arco emocional" ya usado en la landing (ANSIEDAD→CONFIANZA) |
| 4 | **CTA de captura de lead** | Justo debajo del resultado: "Recibe seguimiento de la condición de tu perro" / "Entérate cuando ARES esté disponible" + campo de email + checkbox GDPR | Aparece con ligero delay tras el reveal del resultado (GSAP timeline), para que el usuario primero procese el resultado y luego vea el CTA — no simultáneo |
| 5 | **Pregunta de perfilado** (opcional, tras el email) | "¿Dónde suele pasear tu perro?" (ciudad/parque vallado, campo o monte sin correa, finca propia) — alimenta `ARES_Validacion_Mercado_v1.md` §5, el dato de perfil de comprador que hoy no existe | Sin animación especial, mantener fricción mínima aquí para no perder conversión ya lograda con el email |

### Copy de apoyo (siguiendo el patrón "Qué ganas → Por qué → En tu día a día" de `TONO_DE_VOZ.md`)
- **Qué ganas:** "Sabes si tu perro come lo que necesita para su tamaño y edad."
- **Por qué:** "Cada raza tiene un peso ideal distinto. ARES lo calcula con datos reales de más de 160 razas."
- **En tu día a día:** "La próxima vez que el veterinario te pregunte por su peso, ya lo sabes."

---

## 3) Página 2 — Sitios Pet-Friendly (buscador por ciudad)

**Objetivo:** utilidad práctica + SEO local + segunda vía de captación. Motor de compra: **Automejora** ("soy un buen dueño que socializa bien a su perro") + utilidad pura.

### Estructura por secciones

| # | Sección | Contenido | Animación sugerida |
|---|---|---|---|
| 1 | **Hero + buscador** | Headline corto tipo "Encuentra dónde llevar a tu perro en [ciudad]". Buscador de ciudad (selector o autocompletado) | Ninguna animación de impacto aquí — prioridad velocidad, el usuario quiere resultados rápido |
| 2 | **Resultados (lista + mapa opcional)** | Cards por sitio: nombre, tipo (bar/restaurante/parque/alojamiento), dirección, badge "admite perros" (como texto/icono, no badge con fondo de color por el anti-patrón) | Stagger reveal de las cards al cargar resultados (mismo patrón ya usado en la sección BIENESTAR de la landing: "Cards stagger + hover 3D" vía GSAP) — reutilizar componente si el diseñador ya lo construyó para la landing principal |
| 3 | **CTA de lista de espera** | Tras los resultados (o tras N búsquedas): mismo mensaje de captura que la Página 1 | Aparece de forma discreta, sin interrumpir la utilidad de la búsqueda — evitar popups intrusivos |

### Nota técnica para el diseñador
Esta página es una **plantilla reutilizable por ciudad** (`/pet-friendly/madrid`, `/pet-friendly/barcelona`, etc.) — no diseñar una página única, diseñar el patrón/componente que se repite. Los datos vienen del extractor (`ARES_Extractor_PetFriendly_v1.md`, vía Apify), no son contenido estático que el diseñador tenga que maquetar caso por caso.

---

## 4) Página 3 — Landing de captura general / "Próximamente"

**Objetivo:** punto de entrada para tráfico directo/campañas + conexión con la preventa. Motor de compra: **Seguridad/Paz mental** (el mismo que domina la landing de venta principal).

### Estructura por secciones

| # | Sección | Contenido | Animación sugerida |
|---|---|---|---|
| 1 | **Hero** | Versión resumida del Hero de `landing/index.html` (mismo headline "ARES" + subhead emocional del PAS ya escrito en `TONO_DE_VOZ.md` §1), pero más corto — esta página no vende el producto completo, invita a apuntarse | Fondo animado con **vanta** o **shadergradient** (ya vendorizados en Pick4Design) — mismo recurso ya contemplado en el brief original para `hero-bg`, reutilizable aquí sin coste adicional de diseño desde cero |
| 2 | **Bloque de expectativa** | 2-3 líneas de qué está por venir (localización + salud + nutrición, sin entrar en despiece técnico completo — eso ya vive en la landing de venta) | Fade-in simple, sin necesidad del scroll-driven complejo de la landing de venta |
| 3 | **Formulario de lista de espera** | Mismo mecanismo de captura que las páginas 1 y 2 — email + GDPR | Consistente visualmente con las otras 2 páginas para que el usuario reconozca el mismo punto de conversión en cualquiera de las 3 |
| 4 | **Enlace a la landing de venta completa** | Para quien quiera ver el producto completo ya existente (`landing/index.html`) | Sin animación especial, es un link de salida |

**Nota de negocio:** esta página sustituye/complementa el canal "grupo de WhatsApp de deportistas" del roadmap de preventa original (Mes 1: 5 unidades) — ya señalado como desalineado con el ICP actual de salud/bienestar en la sesión anterior.

---

## 5) Mecanismo de captura de leads — especificación técnica (sin cambios de v1.0)

- **Un único punto de captura de datos** alimentado desde las 3 páginas.
- **Campos mínimos:** email (obligatorio) + campo de perfilado opcional (Página 1).
- **Plataforma de email marketing:** pendiente de decisión (Mailchimp/Brevo/ConvertKit).
- **GDPR:** checkbox de consentimiento explícito, no opt-in implícito.

## 6) Qué NO se especifica aquí (sigue pendiente)
- Wireframes/maquetas visuales concretas (trabajo del diseñador a partir de esta especificación).
- Blog/guías (fase 2, ver `ARES_Estrategia_Contenido_Comunidad_v1.md` §5).
- Backend/infraestructura de la página Pet-Friendly (ver `ARES_Extractor_PetFriendly_v1.md`).
- Decisión final sobre qué recursos "opcionales" de Pick4Design (rough-notation, liquid-glass-js) se usan realmente — quedan sujetos a validación contra el anti-patrón de marca antes de implementarlos.
