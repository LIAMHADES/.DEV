# ANIMACIONES ARES FOR CLAUDE — Página Descanso

**Creado por:** OpenCode (deepseek-v4-pro)  
**Fecha:** 2026-08-01  
**Para:** Claude Code (GSAP + diseño visual)

---

## PALETA DE COLORES — USAR TODOS

Las 2 animaciones deben integrar la paleta completa de la página para tener personalidad visual. No usar solo azul — mezclar los 4 colores + blanco:

| Token | Hex | Rol en las animaciones |
|-------|-----|------------------------|
| `--deco` / `--t` | `#86bbd8` / `#f0f2f5` | **Azul cielo** — reposo tranquilo, barras base, arcos de sueño, texto principal |
| `--bg` / `--bg2` | `#151d25` / `#1c2732` | **Azul marino** — fondos, anillo exterior del reloj, centro del donut |
| `--cta` | `#f26419` | **Naranja** — acentos de alerta, puntos de atención |
| `--hl` | `#f6ae2d` | **Amarillo dorado** — inquietud, marcas de paseo, highlights, brillo |
| `--t` | `#f0f2f5` | **Blanco** — texto, labels, números del centro del reloj |

**Regla**: no usar un solo color. El azul cielo es el tono base, pero las animaciones deben tener toques de naranja (alerta), dorado (movimiento) y blanco (legibilidad).

---

## 1. GRÁFICO DE BARRAS — NOCHE INQUIETA

**Ruta en el DOM:** `/html/body/section[2]/div/div[3]/div[1]`

**Selector CSS:** `#como-funciona .hf-chart`

### Estado actual
17 barras CSS (`div.hf-bar`) con alturas fijas en porcentaje:
- Barras normales: gradiente azul cielo (`rgba(134,187,216,0.2)` → `rgba(134,187,216,0.5)`)
- 3 barras de alerta (`.hf-bar-alert`): gradiente dorado + `box-shadow:0 0 8px rgba(246,174,45,0.3)`
- Badge "INQUIETUD DETECTADA": borde dorado con fondo semi-transparente

### Lo que hemos probado (y descartado)
1. **SVG puro a mano** — `<rect>` uno a uno con coordenadas Y calculadas. Quedaba muy cutre, sin personalidad.
2. **CSS bars estático** (actual) — mejor que SVG pero sin vida. No reacciona al scroll.

### Cómo queremos que se vea
- **Animación de entrada con GSAP ScrollTrigger**: las barras crecen desde altura 0 hasta su valor final. Efecto "crecimiento" secuencial (stagger 0.06s).
- **Barras de reposo (azul cielo → azul marino)**: `fromTo` con `scaleY:0 → 1`, `transformOrigin: 'bottom'`, ease `power2.out`.
- **Barras de inquietud (dorado con glow naranja)**: overshoot con `back.out(2)` + pulso sutil después de aparecer.
- **Badge**: fade-in + slide-up con delay 0.5s, color dorado con texto blanco.
- **Colores integrados**: azul cielo base, dorado en las 3 barras de alerta, naranja en el glow del badge.

```js
gsap.fromTo('.hf-bar', { scaleY: 0, transformOrigin: 'bottom' },
  { scaleY: 1, stagger: 0.06, duration: 0.7, ease: 'power2.out',
    scrollTrigger: { trigger: '#como-funciona', start: 'top 70%', once: true } });

gsap.fromTo('.hf-bar-alert', { scaleY: 0 },
  { scaleY: 1, stagger: 0.1, duration: 0.8, ease: 'back.out(2)', delay: 0.3,
    scrollTrigger: { trigger: '#como-funciona', start: 'top 70%', once: true } });

gsap.fromTo('.hf-alert-badge', { autoAlpha: 0, y: 10 },
  { autoAlpha: 1, y: 0, duration: 0.5, delay: 0.9, ease: 'power2.out',
    scrollTrigger: { trigger: '#como-funciona', start: 'top 70%', once: true } });
```

---

## 2. RELOJ 24H — CÍRCULO DE DESCANSO

**Ruta en el DOM:** `/html/body/section[3]/div/div[3]/div[1]`

**Selector CSS:** `#dia-tipico .dt-ring-svg`

### Estado actual
SVG con 3 arcos y 2 marcas de paseo:
- Arco noche (22h→6h, 120°): azul cielo `rgba(134,187,216,0.45)` con borde `rgba(134,187,216,0.2)`
- Arco siesta mañana (9h→10h, 15°): azul claro `rgba(134,187,216,0.22)`
- Arco siesta tarde (14h→16h, 30°): azul claro `rgba(134,187,216,0.22)`
- Marcas de paseo (`.dt-mark`): dorado `#f6ae2d`, 2 líneas desde el centro, actualmente `opacity:0`
- Centro: círculo azul marino `var(--bg2)` + texto blanco "~14h DE REPOSO"
- Leyenda lateral: dorado, azul cielo, blanco

### Lo que hemos probado (y descartado)
1. **SVG con trigonometría manual** — Los arcos no encajaban. Ángulos mal calculados 3 veces.
2. **CSS conic-gradient** — Los ángulos no se mapean bien a horas de reloj. `::after` tapaba las líneas de paseo.
3. **Barra horizontal 24h** — Funcional pero el usuario prefiere el círculo.
4. **Fade-in básico con GSAP** — Funciona pero es aburrido (solo opacity 0→1).

### Cómo queremos que se vea
- **Efecto "dibujo progresivo"** con `stroke-dasharray` + `stroke-dashoffset`: cada arco se TRAZA desde 0 hasta su longitud total. Como si un lápiz dibujara el sector.
  - Secuencia: noche (azul cielo) → siesta mañana (azul claro) → siesta tarde (azul claro)
  - `ease: 'power2.inOut'`, `duration: 1.2s` cada uno
- **Marcas de paseo**: aparecen como agujas doradas con `scale:0→1` + glow naranja suave, `transformOrigin: '140px 140px'` (centro del SVG).
- **Texto central**: pop-in desde `scale:0.8` con `back.out(1.5)`. Blanco puro.
- **Leyenda lateral**: stagger fade-in sincronizado. Texto blanco con swatches de color.
- **Colores integrados**: azul cielo (arcos base), azul marino (fondo centro), dorado (marcas paseo), naranja (glow puntual), blanco (texto centro + leyenda).

```js
// Arcos: stroke-dasharray trick para dibujo progresivo
document.querySelectorAll('.dt-arc').forEach((arc, i) => {
  const len = arc.getTotalLength();
  gsap.fromTo(arc,
    { strokeDasharray: len, strokeDashoffset: len, opacity: 0 },
    { strokeDashoffset: 0, opacity: 1, duration: 1.2, delay: i * 0.4, ease: 'power2.inOut',
      scrollTrigger: { trigger: '#dia-tipico', start: 'top 70%', once: true } }
  );
});

// Marcas de paseo: clavan desde el centro con efecto "aguja"
gsap.fromTo('.dt-mark', { scale: 0, transformOrigin: '140px 140px', opacity: 0 },
  { scale: 1, opacity: 0.6, stagger: 0.2, duration: 0.6, ease: 'back.out(2)',
    delay: 1.2, scrollTrigger: { trigger: '#dia-tipico', start: 'top 70%', once: true } });

// Texto central: pop
gsap.fromTo('#dia-tipico text', { scale: 0.8, opacity: 0, transformOrigin: '140px 140px' },
  { scale: 1, opacity: 1, duration: 0.7, ease: 'back.out(1.5)', delay: 1.4,
    scrollTrigger: { trigger: '#dia-tipico', start: 'top 70%', once: true } });

// Leyenda: stagger fade-in
gsap.fromTo('.dt-item', { autoAlpha: 0, x: -20 },
  { autoAlpha: 1, x: 0, stagger: 0.12, duration: 0.5, delay: 1.6,
    scrollTrigger: { trigger: '#dia-tipico', start: 'top 70%', once: true } });
```

---

## NOTAS PARA CLAUDE

- GSAP cargado vía CDN en `descanso.html` (línea 10-11): `gsap.min.js` + `ScrollTrigger.min.js`.
- Los SVGs ya existen en el HTML. Solo añadir JS con las animaciones descritas.
- No usar Vanta.js, Three.js ni otras librerías. GSAP puro.
- Respetar `prefers-reduced-motion` con `gsap.matchMedia()`.
- La paleta COMPLETA: azul cielo `#86bbd8`, azul marino `#151d25`/`#1c2732`, naranja `#f26419`, dorado `#f6ae2d`, blanco `#f0f2f5`. USAR TODOS, no solo azul.
