# ARES — Tienda Integrada de Bienestar (v1.0)

**Versión:** 1.0 | **Fecha:** 2026-08-14 | **Estado:** planificado (no implementada) — modelo dropshipping / redirección a la marca

> **Qué es (explicación clara):** una **tienda dentro de ARES** (web y app) donde el usuario encuentra productos para su perro **recomendados según los datos reales de su mascota** (actividad, peso, calorías, alergias). El usuario **ve y compra desde el sitio de ARES**, pero ARES **no guarda stock**: hace de **intermediario (dropshipping)** — cuando alguien compra, ARES pide las unidades al fabricante/marca y el producto se envía directamente al cliente. Es **cero inventario y cero logística propia**.

---

## 1. POR QUÉ ESTE MODELO (dropshipping, sin stock)

| Aspecto | Dropshipping (elegido) | Stock propio (descartado) |
|---|---|---|
| **Inventario** | **Cero** — no compramos ni guardamos productos | Requiere almacén, compra y riesgo de stock |
| **Logística** | El fabricante envía directamente al cliente | Embalaje, envíos, devoluciones |
| **Intermediario** | ARES pide las unidades al fabricante por cada pedido | ARES es vendedor con stock |
| **Riesgo** | Mínimo (no invertimos en producto) | Alto (stock que no se vende, caducidad) |
| **Margen** | Diferencia entre precio de venta y precio del fabricante | Margen mayor pero con costes |
| **Adecuado a ARES ahora** | ✅ Perfecto — sin capital ni infraestructura | ❌ Inviable en esta fase |

**Decisión (2026-08-14):** ARES **nunca guarda stock**. El usuario **ve los productos desde la web o app de ARES** y compra desde allí; ARES **hace de intermediario**: pide las unidades al fabricante (dropshipping) y el producto llega al cliente directo del fabricante. El cliente puede ver la marca del producto, pero **compra en ARES** y ARES gestiona el pedido con el fabricante.

---

## 2. CÓMO FUNCIONA PARA EL USUARIO (experiencia)

1. El usuario abre la **sección Tienda** en la **app o web de ARES**.
2. ARES analiza el perfil del perro (raza, edad, peso, actividad real, alergias) y **recomienda productos**.
3. Cada producto tiene una ficha clara: **qué es, por qué es bueno para TU perro, certificaciones, ingredientes**.
4. El usuario **compra desde ARES** (carrito en la web, pago por web para evitar App Store).
5. ARES **pide las unidades al fabricante** (dropshipping) y el fabricante **envía el producto directo al cliente**.
6. ARES gana la **diferencia** entre el precio de venta y el precio que paga al fabricante.

**Puntos clave para el usuario:**
- Ve los productos en ARES (recomendados con sus datos), pero sabe que el envío llega **directo del fabricante**.
- ARES actúa como **intermediario de confianza**: curó el catálogo y gestiona el pedido.
- El pago se hace en la web de ARES (transparencia, sin comisiones de App Store).

---

## 3. FILOSOFÍA: SOLO PRODUCTOS DE CALIDAD Y BIENESTAR

ARES no vende "cualquier cosa". La tienda está alineada con el eje de producto **salud/bienestar general del perro** (DL-001):

- **Alimentación de calidad** — pienso/húmedo sin rellenos ni subproductos dudosos, con ingredientes trazables.
- **Suplementos con certificación** — solo los validados, con dosificación clara.
- **Cuidado y seguridad** — collares, antiparasitarios seguros, accesorios sin riesgo.
- **Nada de modas o productos sin base** — cada producto pasa una **curaduría previa** antes de entrar.

**Regla de oro:** si un producto no aporta bienestar comprobable al animal, no entra. La reputación de ARES depende de que lo que recomendamos sea bueno.

---

## 4. LO QUE NECESITAMOS PARA MONTARLA (plan por fases)

| Fase | Qué implica | Coste `[EST]` | Tiempo |
|---|---|---|---|
| **A. Curaduría** | Definir criterios de calidad (ingredientes, certificaciones, ausencia de tóxicos). Validar lista con veterinario. | Contenido (500-1000€ o tiempo) | 1-2 meses |
| **B. Partners (afiliación)** | Acuerdos con marcas de pienso/suplementos de calidad → enlace de afiliado con comisión. Sin stock. | ~0€ (acuerdos) | 2-3 meses |
| **C. Catálogo + BD** | Base de datos de productos con nutrición (cruza con Dog Fuel), imágenes, ficha. | ~0-500€ | 1-2 meses |
| **D. Motor de recomendación** | Lógica que cruza perfil del perro + actividad + alergias → sugiere productos. | Desarrollo | 2-3 meses |
| **E. Integración en app** | Sección tienda + enlace de compra externo (redirección a la marca). Pago web. | Desarrollo | 2-3 meses |

> **Nota:** la fase B (partners) puede empezar **antes** que las demás, de forma manual (enlaces de afiliado) sin esperar a la app. La curaduría (A) es la que da calidad — no se salta.

---

## 5. MODELO DE NEGOCIO (monetización)

- **Margen de intermediación (dropshipping):** ARES compra al fabricante y vende al cliente a un precio superior. La diferencia es el margen. `[EST]` típico 10-25% del precio de venta.
- **Sin coste de inventario ni logística** (el fabricante envía directo al cliente).
- **Sin comisión App Store:** el pago se hace en la **web de ARES** (no in-app), evitando el 15-30%.
- **Métricas de éxito:** conversión tienda, ticket medio, % de recomendaciones IA aceptadas, tasa de recompra.

**Ejemplo `[EST]`:** un pienso de 50€ — ARES lo compra al fabricante por ~40€ y lo vende a 50€ → **margen de 10€** sin tocar stock ni logística.

---

## 6. INTEGRACIÓN CON EL EJE DE SALUD

La tienda no es un escaparate suelto — alimenta el ecosistema de salud:

- Cuando el usuario registra un producto nuevo (pienso/suplemento) en la tienda, se añade a su **historial de dietas y peso**.
- El **informe mensual/semanal** refleja qué come y cómo evoluciona su peso con ese producto.
- Las recomendaciones usan los datos reales (actividad, calorías, alergias) → la tienda **refuerza el "cuidado real"**, no es venta a secas.

---

## 7. RIESGOS Y MITIGACIONES

| Riesgo | Mitigación |
|---|---|
| Recomendar un producto malo daña la reputación | **Curaduría rigurosa** + validación veterinaria + revisión periódica del catálogo |
| Producto agotado en el fabricante al hacer el pedido | Acuerdos con fabricantes que garanticen disponibilidad (dropshipping estable); alternativas por categoría |
| El cliente duda de comprar en ARES y recibir del fabricante | **Transparencia:** la app explica el modelo ("compra en ARES, el producto llega directo del fabricante") |
| Dependencia de un fabricante | Varios partners por categoría (no depender de una sola marca) |

---

## 8. RELACIÓN CON OTRAS FEATURES

- **Dog Fuel (nutrición):** la tienda y la base de datos de alimentos comparten catálogo.
- **Historial de dietas y peso:** los productos comprados se registran automáticamente.
- **Superalimentos (Premium):** la guía de "alimentos óptimos" enlaza con productos de la tienda.
- **Aviso de peligros de la zona:** complementa con recomendaciones de antiparasitarios seguros.

---

## 9. ESTADO Y PRÓXIMOS PASOS

- **Estado:** planificado — **NO implementada**. Requiere curaduría + partners antes de construir.
- **Cuándo:** cuando la base de clientes justifique el esfuerzo y haya partners validados.
- **En la web:** la tienda NO aparece en la tabla de precios por ahora (no prometer lo que no está listo). Cuando se lance, se añadirá como "tienda" en Básico/Premium.
