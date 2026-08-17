# ARES LP — Checklist de Decisiones Pendientes

> Ordenados de más urgente a menos urgente

---

## 🟥 PRIORIDAD ALTA (bloquean empezar a escribir código)

### [ ] 1. TIPOGRAFÍA
- ¿Qué fuente para headlines? (bold, atrevida)
- ¿Qué fuente para body? (legible, moderna)
- ¿Qué fuente para datos técnicos?
- **Estado**: Usuario descargando opciones. Dirección: bold, reflejar ARES.

### [ ] 2. TONO DE VOZ — ¿cómo habla ARES?
- **Militar/seco?**: "ARES. Sub-1m. Punto." → serio, técnico, frases cortas.
- **Protector/emocional?**: "Tu perro merece un guardián. No solo un localizador." → mezcla emocional + técnico.
- **Tech/profesional?**: "IoT Direct-to-Cloud con precisión GNSS híbrida Kalman." → muy técnico.
- **Híbrido?**: Emocional en hero y storytelling, técnico en despiece y features.
- **Decisión**: El usuario dijo que quiere storytelling con énfasis en emociones. Pero no hemos cerrado el tono exacto.

### [ ] 3. TEXTO DE CADA SECCIÓN
- **Hero**: ¿Headline exacto? "ARES — El guardián de tu perro" vs "ARES. Precisión que puedes sentir" vs otro.
- **Ansiendad**: ¿Texto exacto del problema?
- **Feature headlines**: 6 títulos para las cards de bienestar (actividad, sueño, geofence, etc.)
- **CTA buttons**: ¿"Reserva tu ARES" o "Consigue el tuyo" o "Empieza a protegerlo"?
- **Planes**: ¿Textos exactos de qué incluye Basic, Premium, Family?

### [ ] 4. TONO DEL DESPIECE — ¿cómo se explica cada capa?
- ¿Técnico puro? → "ESP32-S3 + SIM7000G. LTE-M. GNSS. WiFi. BLE."
- ¿Beneficio puro? → "Sin teléfono. Sin intermediarios. Sin preocupaciones."
- ¿Híbrido? → "LTE-M Direct-to-Cloud. Tu perro conectado aunque tú no estés."

---

## 🟧 PRIORIDAD MEDIA (afectan el diseño visual)

### [ ] 5. LAYOUT EXACTO DE LA PÁGINA
- ¿Ancho máximo del contenedor? → 1200px? 1400px? Full-width en hero?
- ¿Breakpoints exactos? → Desktop (1400+), Tablet (768-1024), Mobile (<768)?
- ¿Grid del despiece? → ¿Sticky vertical o scroll horizontal?

### [ ] 6. CÓMO SE GENERA EL DEVICE-RENDER
- **Opción A**: CSS art (lo dibujo con divs + CSS). 0 dependencias, 0 peso extra, control total.
- **Opción B**: ComfyUI FLUX (imagen realista generada). Mejor calidad visual, pero requiere generarla.
- **Decisión**: El usuario dijo que no tiene dispositivo físico. ¿Preferimos CSS art (estilo técnico/blueprint) o imagen generada por IA (estilo realista)?

### [ ] 7. MODO OSCURO / LIGHT MODE
- ¿Solo modo oscuro o también modo claro?
- La paleta definida usa fondos oscuros (#004E98 como fondo principal). ¿Light mode compatible?

### [ ] 8. BARRA DE PROGRESO
- 2px en top, animada con scroll. ¿Color? (naranja #FF6700)
- ¿Siempre visible o solo al hacer scroll?

---

## 🟨 PRIORIDAD BAJA (pueden decidirse después)

### [ ] 9. FAVICON
- ¿Logo ARES? Se necesita diseñar uno simple (SVG).
- ¿O usar icono de perro + letra A?

### [ ] 10. ANIMACIONES EXACTAS
- Velocidades de cada animación (transiciones de 0.6s? 0.8s? 1.2s?)
- Stagger delays (cada 80ms? 100ms? 120ms?)
- Curvas `cubic-bezier` para cada efecto
- Podemos decidir sobre la marcha mientras escribimos el código.

### [ ] 11. PERFORMANCE BUDGET
- Peso máximo total de la página (¿500KB? ¿1MB?)
- ¿Cuántas fuentes cargar? Google Fonts pesa.

### [ ] 12. SEO / META TAGS
- Title, description, og:image
- Partir del texto que decidamos en las secciones.

---

## Resumen

| Prioridad | Items | Bloquea código |
|:---------:|-------|:--------------:|
| 🟥 Alta | Tipografía, Tono de voz, Texto secciones, Tono despiece | SÍ |
| 🟧 Media | Layout, Device render, Dark/light, Barra progreso | Parcial |
| 🟨 Baja | Favicon, Animaciones, Performance, SEO | No |

**Siguiente paso**: Elige qué item quieres cerrar ahora. Recomiendo:
1. **Tono de voz** (rápido, decidimos cómo habla ARES)
2. **Textos de sección** (el contenido real de la página)
3. **Tipografía** (cuando tengas las fuentes)
