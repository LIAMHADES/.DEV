# ARES v4.0 — Extractor Automatizado de Sitios Pet-Friendly
**Versión:** 1.0 | **Estado:** aprobado por el usuario, automatizado desde el MVP (no curado a mano). Usa **Apify** (clave ya disponible en `C:\Users\solde\.secrets\00_SECRETS_AND_MCP.md` del ecosistema — no se expone el valor aquí por protocolo de seguridad del proyecto, solo se referencia su ubicación).

---

## 1) Decisión: Apify en vez de OSM Overpass API

**Cambio respecto al primer planteamiento:** se había propuesto OpenStreetMap Overpass API como fuente primaria por ser gratuita y sin necesidad de API key. El usuario confirmó que ya se dispone de cuenta y clave de **Apify**, lo que cambia la recomendación — Apify tiene un actor ya construido ("Google Maps Search Scraper" / "Google Maps Scraper") que resuelve exactamente este caso de uso sin tener que construir el pipeline de normalización de datos desde cero:

- Extrae de Google Maps: nombre, dirección, teléfono, web, valoración, número de reseñas, horario, coordenadas GPS, y **categoría del negocio** (bar, restaurante, parque, alojamiento, etc.) — 20+ campos por resultado.
- Funciona por **búsqueda de palabra clave + ubicación** (ej. "restaurante pet friendly" + "Madrid"), sin necesitar API key de Google Places (que sí tiene coste y cuotas más restrictivas).
- **Coste:** ~$0,016 por consulta, con los primeros ~40 resultados gratis por búsqueda — muy asequible para el volumen de un MVP de 3-5 ciudades.
- No requiere construir lógica de scraping/parsing propia — es un servicio ya empaquetado, se integra vía API de Apify.

**OSM Overpass queda como fuente secundaria/complementaria** (fase 2): útil para parques y zonas de juego específicamente etiquetadas como "dog friendly" en OSM, que Google Maps no siempre categoriza bien como tal — se puede combinar más adelante, pero no es necesaria para el MVP.

## 2) Pipeline técnico propuesto (MVP)

1. **Búsquedas por ciudad y categoría:** para cada ciudad del MVP (Madrid, Barcelona, Valencia + 1-2 a decidir), ejecutar búsquedas del actor de Apify con keywords tipo:
   - "restaurante admite perros [ciudad]"
   - "bar pet friendly [ciudad]"
   - "parque para perros [ciudad]"
   - "alojamiento pet friendly [ciudad]" (para la fase de viajes/vacaciones con el perro, si se decide incluir)
2. **Normalización:** mapear los 20+ campos que devuelve Apify a un esquema simple para la web: `nombre, direccion, ciudad, tipo (bar/restaurante/parque/alojamiento), lat, lon, telefono (opcional), web (opcional), fuente=apify`.
3. **Deduplicación:** un mismo negocio puede aparecer en varias búsquedas (ej. un bar puede salir tanto en "bar pet friendly" como en "restaurante admite perros") — deduplicar por nombre+dirección antes de guardar.
4. **Almacenamiento:** nueva tabla en la base de datos del backend (hoy no existe ninguna tabla de este tipo — `db/` está vacío, ver Risk Register de la sesión anterior sobre falta de migraciones versionadas). Se recomienda crear esta tabla ya con migraciones versionadas (Alembic u otra herramienta), aprovechando para resolver ese gap de higiene técnica de paso.
5. **Exposición:** endpoint del backend que la Página 2 (buscador pet-friendly, ver `ARES_Especificacion_Web_v1.md`) consulta por ciudad.
6. **Actualización periódica:** las búsquedas de Apify no son en tiempo real — se recomienda una tarea programada (ej. mensual) que re-ejecute las búsquedas por ciudad para mantener los datos razonablemente frescos (nuevos negocios, cierres).

## 3) Complemento con skills de scraping ya instaladas (enriquecimiento, no fuente primaria)

Para negocios/lugares que no aparezcan bien categorizados en Google Maps pero sí estén mencionados en contenido editorial (ej. un blog local "los 10 mejores bares para ir con tu perro en Valencia"), se puede usar como fuente de enriquecimiento (no primaria):
- **`site-crawler`** (skill ya instalada): crawler ligero para extraer contenido de blogs/directorios locales sobre sitios pet-friendly.
- **`scrapy-web-scraping`** (skill ya instalada): si algún directorio específico requiere paginación o JS pesado, usar este framework más robusto en vez del crawler simple.

Esto queda como **fase 2**, después de validar que la fuente Apify/Google Maps ya cubre un volumen razonable de resultados en las ciudades del MVP.

## 4) MVP de ciudades y alcance inicial

- **Fase 1 (MVP):** Madrid, Barcelona, Valencia — las 3 ciudades más grandes, mayor volumen de búsqueda esperado.
- **Fase 2:** ampliar a 5-10 ciudades más según demanda real observada en la página (qué ciudades busca la gente que no está todavía cubierta — esto se puede medir directamente en la Página 2 de la web si se registra el término de búsqueda cuando no hay resultados).

## 5) Pendiente de decisión / acción
1. Confirmar el actor exacto de Apify a usar (hay varios "Google Maps Scraper" de distintos autores en el marketplace de Apify con precios ligeramente distintos — comparar antes de comprometer presupuesto de scraping).
2. Decidir si el endpoint de resultados vive en el backend ya existente (`app/routes/`) o en un servicio aparte, dado que es una pieza de infraestructura nueva no directamente ligada al tracking del dispositivo.
3. Crear la tabla de BD con migraciones versionadas (gap ya señalado en el Risk Register de la sesión anterior) en vez de añadirla sin control de versiones como el resto del esquema actual.
