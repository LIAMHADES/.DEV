# ARES v4.0 — Especificación de Página de Pricing/Suscripciones (para diseñador)
**Versión:** 1.0 | **Motivo:** el usuario detectó que no existe ninguna página que explique el pricing completo (hardware + planes de suscripción) — hoy `index.html` solo muestra 3 cards genéricas (BASIC/PREMIUM/FAMILY) sin detalle real, mientras que la especificación completa de qué incluye cada plan ya está documentada en `ARES_planes_basico_vs_premium_v1.md` y `01_PRODUCTO_Y_NEGOCIO.md` §3.7 (sesión anterior) y nunca se ha traducido a una página web.

---

## 1) Por qué esta página es necesaria

`index.html` §Planes hoy muestra 3 tarjetas con ~6 bullets cada una — insuficiente para una decisión de compra que ya identificamos como "extraordinaria" (el hardware cuesta 1,6x el presupuesto anual típico de la categoría "accesorios", ver `ARES_Validacion_Mercado_v1.md` §2.1). Una decisión de ese tamaño necesita una página dedicada que resuelva dudas de precio antes de que el usuario abandone.

## 2) Contenido ya cerrado a reutilizar (no inventar nada nuevo aquí)

Fuente de verdad: `ARES_planes_basico_vs_premium_v1.md` (contenido íntegro de planes) + `01_PRODUCTO_Y_NEGOCIO.md` §3.5/§3.7 (precios de hardware y Plan Esencial) + Decision Log DL-008 (Plan Esencial fijado en 5€/mes).

### 2.1 Estructura de precios a mostrar

**Hardware (pago único) — PVP v2.0 (2026-08-14):**
| SKU | Precio | Batería |
|---|---|---|
| ARES Medium | 120€ | ~2750mAh, ~18-20 días uso típico |
| ARES Large | 149€ | ~4000mAh, ~26-28 días uso típico |
| Family Pack (cualquier combinación) | desde 199€ (2× Medium) | — |

**Suscripción (mensual, obligatoria pero mínima) — v2.1 (2026-08-14):**
| Plan | Precio | Qué resuelve |
|---|---|---|
| **Esencial** | 6€/mes (60€/año) | Localización fiable, historial 7 días, lo indispensable, cubre el coste real de conectividad con margen |
| **Básico/Standard** | 10€/mes (100€/año) | Historial 30 días, 5 zonas seguras, 5 compartidos, informe de salud mensual (PDF) + exportación PDF+GPX, benchmarks por raza, historial de dietas y peso, guía de alimentos, informe de batería, score de bienestar diario, registro de medicación, guía de ejercicio, alerta de golpe de calor, mapas offline |
| **Premium** | 12,99€/mes (129,90€/año) | Todo lo de Básico + informe de salud semanal + estadísticas diarias, multi-mascota, rankings nacionales, historial 1 año, nutrición avanzada (dieta personalizada, macros IA, superalimentos), aviso de peligros de la zona, chat veterinario, plan de salud preventivo, modo cachorro/senior, análisis rascado/ladridos, fatiga/recuperación, edad biológica |

**Nota importante para el diseñador/negocio:** los precios v2.1 están cerrados (6/10/12,99€). El anclaje: Básico→Premium = +2,99€ (empuja a Premium). **El pago se realiza siempre vía web** (evita 15-30% de App Store/Google Play).

**Add-ons (ya documentados, precios cerrados):**
- Travel/Roaming Pass: 5,99€/mes (UE/EEE) o 9,99€/mes (Global)
- Historial extendido (para Básico): +2,99€/mes
- Live Share Pro (para Básico): +2,99€/mes
- Seguro (pago único, escalonado): **+2 años = 19,99€** · **+3 años = 25€** (reposición al 50% del dispositivo nuevo tras la garantía legal)

### 2.2 Tabla comparativa de features (contenido íntegro ya escrito)
Todo el detalle de qué incluye cada plan (localización, geofencing, salud/actividad, social, nutrición) está en `ARES_planes_basico_vs_premium_v1.md` secciones 1 y 2 — la página debe presentar esto como tabla comparativa Esencial vs. Básico vs. Premium, no como texto corrido. Se recomienda extraer los bullets ya redactados en ese documento tal cual, sin reescribirlos.

## 3) Estructura de la página (secciones)

| # | Sección | Contenido |
|---|---|---|
| 1 | **Hero** | Headline directo tipo "Elige el nivel de tranquilidad que necesitas" — motor de compra Seguridad/Automejora, tono `TONO_DE_VOZ.md` |
| 2 | **Selector de hardware** | Cards de Medium/Large/Family Pack (precio, batería, para qué perro es ideal cada uno) — reutilizar el patrón visual ya usado en `index.html` para las cards de planes |
| 3 | **Tabla comparativa de suscripción** | Esencial / Básico / Premium en columnas, features en filas — el bloque central de la página |
| 4 | **Explicación de por qué hay coste de suscripción** (transparencia) | Usar el principio ya documentado: "no hay plan 100% gratis porque la conectividad celular tiene un coste real" — esto es honestidad de marca, coherente con el motor "Curiosidad/Escepticismo" de `TONO_DE_VOZ.md` ("la mayoría de trackers mienten... nosotros te explicamos el coste real") |
| 5 | **Add-ons** | Travel Pass, Live Share Pro, Seguro — como sección secundaria/expandible, no compitiendo visualmente con los planes principales |
| 6 | **FAQ de pricing** | Preguntas tipo "¿Puedo cambiar de plan luego?", "¿Qué pasa si no pago la suscripción?", "¿Hay permanencia?" — contenido a redactar, no existe todavía (ver pendientes) |
| 7 | **CTA final** | "Reserva tu ARES" — mismo CTA ya usado en `index.html`, o enlace al cuestionario de preventa (`proximamente.html`) si el hardware aún no está en venta real |

## 4) Enlazado (coherente con la ronda de enlaces ya en curso)
- Esta página sustituye/amplía la sección `#planes` de `index.html` — se recomienda que las 3 cards actuales de `#planes` enlacen "Ver todos los detalles" hacia esta nueva página en vez de (o además de) el CTA directo "Reserva tu ARES".
- Entra también en el dropdown de menú "Recursos" ya en construcción, o como ítem propio del nav si se considera lo bastante importante (recomendado: ítem propio "Precios" en el nav principal, dado que el usuario ya señaló que es "una parte muy importante del proyecto").

## 5) Pendiente de decisión (no asumido aquí)
1. **Precio numérico de los planes Básico y Premium** — solo Esencial (5€/mes) está cerrado. **Decisión del usuario: construir la página con precios PLACEHOLDER** (ej. "9,99€/mes", claramente marcado como cifra provisional en el código/comentario para el diseñador) — no bloquea el resto del trabajo, se sustituye cuando el usuario decida la cifra final.
2. **Contenido del FAQ de pricing** — no existe todavía, hay que redactarlo (permanencia, cambios de plan, cancelación). Usar contenido genérico placeholder razonable por ahora, marcado igual como provisional.
3. **Confirmar si Family Pack incluye descuento en suscripción** (hoy solo se documenta descuento en hardware, desde 199€ por 2 unidades) — no está definido si la suscripción también tiene tarifa familiar. Placeholder: asumir que no hay descuento de suscripción familiar hasta decisión explícita.
