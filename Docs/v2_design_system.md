# Design System — v2 "Warm Tech"

> Diseño activo para V_DOWNLOADER y portfolio personal LIAMHADES.DEV.
> Calidez técnica. Profesional pero accesible.

## Color Palette

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--bg` | `#faf7f2` | `#100e0d` | Fondo general |
| `--bg-card` | `#ffffff` | `#1c1816` | Cards y superficies |
| `--bg-elevated` | `#f5f1ea` | `#241f1c` | Elementos elevados |
| `--bg-input` | `#faf7f2` | `#181512` | Inputs |
| `--terracotta` | `#e0451b` | `#e85a34` | Acción principal, acento |
| `--terracotta-h` | `#f05a32` | `#f0704e` | Hover del acento |
| `--terracotta-g` | `rgba(224,69,27,0.06)` | `rgba(232,90,52,0.10)` | Glow / fondo de acento |
| `--green` | `#5b8c3e` | `#7a9e5a` | Estados ok |
| `--text` | `#1a1512` | `#f5f0ea` | Texto principal |
| `--text-dim` | `#6b6158` | `#e8e0d8` | Texto secundario |
| `--text-faint` | `#9e9186` | `#c8c0b8` | Texto tenue |
| `--border` | `#e6dfd4` | `rgba(255,255,255,0.08)` | Bordes |
| `--border-hover` | `#d4c8b4` | `rgba(255,255,255,0.15)` | Bordes hover |
| `--radius` | `12px` | `12px` | Bordes grandes |
| `--radius-sm` | `6px` | `6px` | Bordes pequeños |

## Typography

| Rol | Fuente | Uso |
|-----|--------|-----|
| Display | `Playfair Display` (Google Fonts, wght 700-800) | H1, hero, títulos grandes |
| Body | `Inter` (Google Fonts, wght 400-600) | Cuerpo, UI, botones, etiquetas |
| Mono | `JetBrains Mono` / `Cascadia Code` / `Consolas` | Código, timestamps, datos |

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600&family=Playfair+Display:ital,wght@0,700;0,800;1,700&display=swap');
```

## Background System

Dos imágenes de fondo intercambiables por tema:

| Tema | Archivo | Overlay |
|------|---------|---------|
| Light | `bg-light.png` | `body::before { background:#18191B; opacity:0.20 }` |
| Dark | `bg-dark.png` | `body::before { background:#18191B; opacity:0.55 }` |

```
html { background:#fff; }
html.dark { background:#000; }
body { background-image:url('./bg-light.png'); background-size:cover; }
html.dark body { background-image:url('./bg-dark.png'); }
```

## Ambient Glow

Dos círculos grandes con `filter:blur(120px)`:

```css
.ambient-1 { width:600px; height:600px; background:rgba(224,69,27,0.10); top:-200px; right:-200px; }
.ambient-2 { width:500px; height:500px; background:rgba(91,140,62,0.07); bottom:-100px; left:-150px; }
```

## Glass Effect (Backdrop Blur)

Todos los elementos con fondo semitransparente usan `backdrop-filter:blur()`.

```css
.card {
  background:rgba(255,255,255,0.88);
  backdrop-filter:blur(10px);
  -webkit-backdrop-filter:blur(10px);
}
html.dark .card { background:rgba(255,255,255,0.04); }
```

Aplicado a: cards, buttons, badges, drop-zone, studio-card, download-item, timeline, style-bar, lang-picker, url-input, presets, segments, theme-btn.

## Theme Toggle

ON/OFF switch fijo (top-left), `localStorage("vdownloader-theme")`.

```css
.theme-btn { position:fixed; top:12px; left:12px; z-index:999; ... }
.theme-knob { ... }
html.dark .theme-knob { margin-left:20px; }
```

## Animaciones

| Animación | Elemento | Descripción |
|-----------|----------|-------------|
| `word-rise` | `.hero-word` | Entrada desde abajo con stagger |
| `underline-draw` | `.hero-underline path` | Línea SVG se dibuja de izq a der |
| `stageIn` | `.stage` | Fade + translateY en secciones |

```css
@keyframes word-rise {
  0% { opacity:0; transform:translateY(.55em); }
  to { opacity:1; transform:translateY(0); }
}
@keyframes underline-draw {
  to { stroke-dashoffset:0; }
}
@keyframes stageIn {
  from { opacity:0; transform:translateY(8px); }
  to { opacity:1; transform:translateY(0); }
}
```

## Botones

```css
.btn {
  padding:7px 14px; border-radius:6px;
  font-family:Inter; font-size:0.72rem; font-weight:500;
  border:1px solid var(--border);
  background:rgba(255,255,255,0.88);
  backdrop-filter:blur(8px);
}
.btn-primary { background:var(--terracotta); color:#fff; }
.btn-primary:hover { text-shadow:0 0 6px rgba(255,255,255,0.4); }
.btn-download { background:var(--terracotta); color:#fff; padding:10px 24px; }
```

## Scrollbar

```css
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { display:none; }
::-webkit-scrollbar-thumb { background:rgba(224,69,27,0.35); border-radius:3px; }
* { scrollbar-width:thin; scrollbar-color:rgba(224,69,27,0.35) transparent; }
```

## Mood

Técnico pero cálido. Profesional, accesible. No minimalista frío ni editorial clásico.
Un término medio entre herramienta funcional y diseño cuidado.
Apropiado para: apps, portfolios técnicos, dashboards, herramientas developer.
