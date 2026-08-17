\## L) Privacidad y cumplimiento (UE) — definición final (v1) + costes (mapa propio + “ayuda búsqueda”)



\### 1) Privacidad mínima (sin sustos)



\*\*Social / ranking\*\*



\* El ranking y cualquier social muestran \*\*solo alias\*\*, nunca nombre real por defecto.

\* En social solo se muestran \*\*métricas agregadas\*\* (km/minutos/badges). \*\*Nunca\*\* puntos exactos ni rutas completas.



\*\*Rutas exactas\*\*



\* \*\*Rutas exactas + histórico detallado\*\*: \*\*solo Owner y Family\*\*.

\* Cualquier tercero (incluido “amigo que ayuda”) \*\*no ve histórico\*\* ni rutas pasadas.



\*\*Modo privado\*\*



\* Toggle “Modo privado” (por perro):



&nbsp; \* No aparece en ranking/social.

&nbsp; \* Mantiene todas las funciones de seguridad.



\*\*Minimización\*\*



\* El “modo ayuda” expone el \*\*mínimo\*\*: ubicación actual (lat/lon), precisión, última actualización, y distancia/rumbo desde el móvil del helper.



---



\### 2) Retención y borrado (GDPR) — por plan



\*\*Retención de histórico (geodatos)\*\*



\* \*\*Básico:\*\* 7 días.

\* \*\*Premium:\*\* 1 año.



\*\*Borrado\*\*



\* “Eliminar cuenta” (borrado total, con ventana técnica de backups).

\* “Eliminar perro” (borra perfil + histórico/sesiones asociados).

\* Revocación inmediata de permisos compartidos (Family) y de accesos de “ayuda”.



\*\*Consentimientos\*\*



\* Marketing/email \*\*opt-in separado\*\*.

\* Tracking/ubicación: texto claro de finalidad (seguridad/servicio) + política de privacidad.



---



\### 3) Compartir ubicación “modo ayuda” (12h) — SOLO con nuestra app (sin credenciales)



\*\*Objetivo\*\*



\* Que el owner pueda pedir ayuda rápida a terceros \*\*sin que el tracker gaste más batería\*\* y sin depender de WhatsApp/Telegram como canal de ubicación (solo como canal de envío del link).



\*\*Principio técnico (tal como lo quieres)\*\*



\* El \*\*dispositivo envía UNA vez\*\* a la central con su cadencia normal.

\* La \*\*central re-emite esa misma ubicación\*\* a todos los móviles que estén en “modo ayuda”.

\* Por tanto: \*\*más helpers = no más batería del tracker\*\*. Solo más tráfico en backend/mapa.



\#### 3.1 Flujo UX (sin login)



1\. Owner activa “Compartir búsqueda” en la app.

2\. Backend genera un \*\*token de ayuda\*\* (aleatorio, no adivinable) con:



&nbsp;  \* `expires\_at = 12h`

&nbsp;  \* `scope = solo lectura (live location)`

&nbsp;  \* `max\_helpers` (límite según plan/upsell)

3\. Owner envía el link por WhatsApp (o donde sea).

4\. El helper instala la app si no la tiene.

5\. Al abrir el link, la app entra directo a \*\*“Mapa fácil (Helper Mode)”\*\*:



&nbsp;  \* Ve ubicación del perro + su propia ubicación (para acercarse)

&nbsp;  \* No ve rutas, no ve histórico, no ve datos personales, no toca ajustes

6\. El Owner puede \*\*revocar\*\* el modo ayuda en cualquier momento.



\*\*Aviso obligatorio en UI\*\*



\* “Este enlace comparte ubicación exacta durante 12h. Compártelo solo con personas de confianza. Puedes revocarlo cuando quieras.”



\#### 3.2 Permisos (roles)



\* \*\*Owner/Family:\*\* control total; pueden crear y revocar el modo ayuda.

\* \*\*Helper (sin credenciales):\*\* solo lectura “ubicación live” + su posición. Nada más.



---



\### 4) Límites y upsell (control de riesgo y de coste)



Aquí se define exactamente lo que pediste (base + upsell), sin crear un tercer plan:



\* \*\*Incluido (Básico y Premium):\*\* hasta \*\*5 helpers simultáneos\*\* en modo ayuda (token activo 12h).

\* \*\*Upsell “Búsqueda en equipo”:\*\* sube a \*\*10 helpers simultáneos\*\*.



> Motivo: el coste marginal real de 5→10 en mapa propio es muy bajo; el límite es por \*\*seguridad/abuso\*\* y por \*\*valor de producto\*\*.



---



\### 5) Mapa propio (self-host) — cómo se hace y por qué



\*\*No se usan tiles de `tile.openstreetmap.org`\*\* porque el uso offline/prefetch está prohibido y el heavy use se bloquea; la política recomienda self-host o proveedor adecuado. (\[Grupo de Operaciones OSMF]\[1])



\*\*Opción A (la que elegiste, correcta):\*\*



\* Servimos \*\*vector tiles propios\*\* desde nuestra infraestructura (objeto + CDN).

\* En la app renderizamos el mapa y solo descargamos tiles de la zona visible.

\* Implementación muy práctica: enfoque tipo “mapa del mundo en un fichero” estilo Protomaps (vector tiles en un archivo estático con HTTP range requests). (\[Protomaps]\[2])



---



\### 6) Coste real de “compartir con 5 vs 10” (con mapa propio)



El coste variable viene sobre todo de \*\*peticiones de tiles\*\* (no del tracker), y se reduce mucho con caché.



Para estimar, uso referencias típicas de vector tiles:



\* Recomendación histórica: \*\*tile medio < 50KB\*\* y límite clásico \*\*500KB\*\*. (\[Medium]\[3])



\#### 6.1 Coste de almacenamiento del mapa mundial (fijo mensual)



Si alojamos el mapa mundial en un único MBTiles grande:



\* R2 Storage: \*\*$0.015/GB-mes\*\* (Standard). (\[Cloudflare Docs]\[4])

&nbsp; Ejemplo con 128GB: \*\*~$1.92/mes\*\* (orden de magnitud). \*(El tamaño exacto depende del estilo/dataset; Protomaps lo plantea como “mundo en un file”, pero el peso final lo decidimos nosotros.)\* (\[Protomaps]\[2])



\#### 6.2 Coste por una búsqueda (variable por helpers)



Si usamos Cloudflare R2:



\* Lecturas (Class B): \*\*$0.36 / millón requests\*\*

\* Egress a Internet: \*\*gratis\*\* (\[Cloudflare Docs]\[4])



\*\*Escenario típico (búsqueda real 30–45 min, poco paneo):\*\*



\* Suposición: ~200 tiles por helper (carga + algo de movimiento).

\* 5 helpers → 1,000 requests → 1,000/1,000,000 × $0.36 = \*\*$0.00036\*\*

\* 10 helpers → 2,000 requests → \*\*$0.00072\*\*



\*\*Escenario heavy (12h, bastante paneo):\*\*



\* Suposición: 4,800 tiles/helper (alto).

\* 5 helpers → 24,000 requests → \*\*$0.00864\*\*

\* 10 helpers → 48,000 requests → \*\*$0.01728\*\*



\*\*Conclusión:\*\* con mapa propio + R2, el salto de 5→10 helpers cuesta \*\*céntimos o menos\*\* por evento incluso en casos “heavy”. El límite/upsell se justifica más por \*\*seguridad y valor\*\*, no por coste puro. (\[Cloudflare Docs]\[4])



---



\### 7) Precio recomendado del upsell (para fijarlo ya)



Como el coste marginal es bajísimo y el valor es alto (“encontrar al perro”), el pricing debe ser \*\*value-based\*\*.



Recomendación (simple y sin fricción en emergencia):



\* \*\*Upsell “Búsqueda en equipo (10 helpers)” = 2,99 €/mes\*\*



&nbsp; \* Evita cobrar “por activación” justo cuando hay urgencia.

&nbsp; \* Mantiene margen incluso con picos.



\*(Si algún día quieres un “Pro” de 20 helpers, sería otro add-on, pero 10 cubre la mayoría de escenarios reales.)\*



---



\### 8) Controles anti-abuso (obligatorios)



\* Token aleatorio largo + expiración 12h + revocación inmediata.

\* 1 token activo por perro (para no proliferar links).

\* Rate-limit por token/IP en backend (evita scraping).

\* Helper Mode \*\*solo lectura\*\* y sin histórico.

\* Log de seguridad mínimo (sin rutas completas) para detectar abuso.



---



Este bloque L queda listo para copiar/guardar como especificación de privacidad + GDPR + “modo ayuda” solo app + mapa propio + costes + upsell.



\[1]: https://operations.osmfoundation.org/policies/tiles/?utm\_source=chatgpt.com "Tile Usage Policy"

\[2]: https://protomaps.com/?utm\_source=chatgpt.com "Protomaps - The open source map in a file"

\[3]: https://medium.com/%40ibesora/a-data-driven-journey-through-vector-tile-optimization-4a1dbd4f3a27?utm\_source=chatgpt.com "A data-driven journey through Vector Tile optimization"

\[4]: https://developers.cloudflare.com/r2/pricing/?utm\_source=chatgpt.com "R2 pricing"



