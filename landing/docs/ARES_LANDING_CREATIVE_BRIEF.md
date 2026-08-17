# ARES GPS — Landing Page — Creative Brief

**Fecha**: 2026-07-21 | **Agente**: OpenCode | **Fase**: Definición

---

## 1. Paleta de Colores — Grupo 3: Calma Natural

| Token | Hex | Rol | % |
|-------|-----|-----|:---:|
| Gris carbón oscuro | `#454851` | Fondo principal, body | 60% |
| Gris oscuro | `#383b43` | Secciones secundarias | — |
| Gris profundo | `#2e3038` | Secciones oscuras, footer | — |
| Verde salvia | `#7BAE7F` | CTAs, highlights, acentos | 10% |
| Verde menta claro | `#95D7AE` | Hover states | — |
| Verde oliva | `#73956F` | Cards, superficies (sutil) | — |
| Blanco lila | `#FCEFF9` | Texto principal | 30% |
| Blanco lila 55% | rgba | Texto secundario | — |

**Psicología**: Los verdes evocan naturaleza, bienestar, salud, equilibrio. El gris carbón aporta seriedad y tecnología. Juntos: "naturaleza + precisión".

---

## 2. Tipografía — DEFINIDO

| Rol | Fuente | Archivo | Peso |
|-----|--------|---------|------|
| **Headlines (h1, h2)** | **Badeen Display** | `BadeenDisplay-Regular.ttf` | Regular |
| **Subtítulos (h3, h4, labels)** | **Bruno Ace SC** | `BrunoAceSC-Regular.ttf` | Regular |
| **Body, párrafos** | **Orbitron** | `Orbitron-Medium.ttf` | Medium |
| **Datos técnicos** | **JetBrains Mono** | Google Fonts CDN | 400 |

**Psicología**: Badeen Display = display bold con carácter. Bruno Ace SC = impacto, mayúsculas, presencia. Orbitron = geométrica, moderna, tech.

---

## 3. Anti-Patrón IA (lo que NO queremos)

- Badges con fondo de color + bordes redondeados → texto limpio sin fondos
- Gradientes arcoiris → sin gradiente o monocromático
- Border-radius > 8px → máximo 4px
- Sombras neón → sombras negras sutiles o sin sombra
- Scrollbar nativo → oculto + barra de progreso fina (2px) en top
- Iconos placeholder genéricos → SVG personalizados o lucide-react

---

## 4. Estilo Visual

- Estética: militar-quirúrgico. Precisión, no decoración.
- Cards: fondo sólido `rgba(58,110,165,0.1)`, borde 1px sutil
- CTAs: sin fondo hasta hover, borde inferior naranja 2px en hover
- Separadores: líneas 1px `rgba(255,255,255,0.06)`
- Imágenes: sin border-radius o máximo 4px

---

## 5. Estructura de Página

### Arco emocional: ANSIEDAD → DESEO → CONFIANZA → PODER → COMUNIDAD → ACCIÓN

| # | Sección | Layout | Emoción | Animación clave |
|---|---------|--------|---------|-----------------|
| 1 | HERO | Fullscreen, texto centrado | Impacto | Scramble text reveal. Fondo CSS + partículas |
| 2 | ANSIEDAD | Split 50/50 | Inquietud | Fade-in texto. Gradiente oscuro animado |
| 3 | CONFIANZA | Imagen FULL + overlay | Alivio | Dispositivo se ilumina progresivamente |
| 4 | DESPIECE | Scroll-driven, 6 capas | Fascinación | ZOOM a cada componente. LEDs se encienden |
| 5 | PRECISIÓN | Centrado + SVG | Certeza | Círculo se reduce 100m→1m |
| 6 | BIENESTAR | Grid 2×3 cards | Seguridad | Cards stagger + hover 3D |
| 7 | PLANES | 3 columnas | Decisión | Reveal escalonado + hover lift |
| 8 | CTA FINAL | Fullscreen + parallax | Urgencia | Footer parallax reveal |

---

## 6. Despiece — 6 Capas

| Capa | Componente | Efecto | Texto informativo |
|------|-----------|--------|-------------------|
| 1 | CARCASA IP68 | Se separa del resto | PENDIENTE |
| 2 | LEDs "L" (×12 SMD 1206) | Página se oscurece. LEDs se encienden uno a uno. Uno late. | PENDIENTE |
| 3 | ANTENA Ignion A101 + LNA | Brillo sutil en antena | PENDIENTE |
| 4 | CEREBRO ESP32-S3 + SIM7000G | Líneas conectan chip → nube | PENDIENTE |
| 5 | SENSORES BMI270 + NTC 10K | Overlay datos perro corriendo | PENDIENTE |
| 6 | BATERÍA + eSIM | Animación intercambio batería | PENDIENTE |

---

## 7. Assets Necesarios

| Archivo | Propósito | Fuente |
|---------|-----------|--------|
| `device-render.png` | Centro del despiece. Capas del dispositivo. | CSS art o ComfyUI |
| `dog-portrait.jpg` | Sección CTA final. Perro mirando a cámara. | Fotos reales del usuario |
| `field-action.jpg` | Sección precisión. Perro corriendo con overlay datos. | Fotos reales del usuario |
| `dashboard-mockup.png` | Prueba social. El producto existe. | Screenshot dashboard React |
| `hero-bg` | Fondo hero. Perro corriendo campo. | CSS fallback ahora → Pika Labs después |
| `precision-circles.svg` | Animación precisión GPS. | Generado por código (SVG inline) |

---

## 8. IA Tools para Generar Assets

| Asset | Herramienta | Coste |
|-------|-------------|:-----:|
| Imagen dispositivo | ComfyUI Cloud (FLUX) o CSS art | 0€ |
| Video perro corriendo | Pika Labs V1.0 (text-to-video) | 0€ |
| Imágenes calidad máxima | LTX-2 (local, open source, 4K) | 0€ |
| Restauración/upscaling | SeedVR2 (local, ByteDance) | 0€ |
