# ARES GPS — Cómo generar assets y animación scroll-synced

## 1. Cómo generar el modelo 3D del producto (GRATIS)

### Herramientas disponibles (HIVE-MIND Rack)

| Herramienta | Tipo | Coste | Resultado |
|-------------|------|:-----:|-----------|
| **ComfyUI + Hunyuan3D** | Local (Windows) | 0€ | Modelo 3D a partir de imagen 2D |
| **ComfyUI + FLUX** | Local (Windows) | 0€ | Imagen del producto (referencia) |
| **LTX-2** | Local (Windows) | 0€ | Video con audio nativo |

### Flujo recomendado:

```
Paso 1: Crear imagen de referencia del producto
  → ComfyUI + FLUX con prompt: "GPS dog tracker device, 
    technical blueprint, isometric view, dark background, 
    rugged waterproof design, LED strip, magnetic charging port"

Paso 2: Convertir imagen a modelo 3D
  → ComfyUI + Hunyuan3D workflow
  → Carga la imagen generada en Paso 1
  → Output: archivo .glb o .obj

Paso 3: Cargar en la web
  → Three.js GLTFLoader
  → Sustituir el mockup actual por el modelo real
  → Mismo sistema de rotación con ratón
```

### Instalación de ComfyUI:

```bash
# Windows: descargar desde comfy.org
# O usar Comfy Cloud (400 créditos/mes gratis, sin instalar nada)
# URL: https://comfy.org
```

---

## 2. Cómo hacer la animación scroll-synced del producto

### Concepto:

La sección VScroll tendrá un producto 3D que se abre/descompone mientras el usuario hace scroll. Los paneles de texto (Aguanta todo, 12 LEDs, etc.) aparecen en momentos específicos del scroll.

### Método: GSAP ScrollTrigger + frames

```
ESTRUCTURA:

<div class="device-pin">  ← position: sticky
  <canvas id="product-canvas">  ← Three.js renderer
</div>

<div class="scroll-panels">  ← flota encima del producto
  <div class="vp">Panel 1</div>
  <div class="vp">Panel 2</div>
  ...
</div>

JS:
// 1. Generar animación del producto (video o secuencia de frames)
// 2. Extraer frames como PNG (ffmpeg o similar)
// 3. Sincronizar con scroll:

const totalFrames = 120; // frames del video
const sectionHeight = 600; // vh equivalentes

ScrollTrigger.create({
  trigger: '#vscroll',
  start: 'top top',
  end: `+=${sectionHeight}vh`,
  pin: true,
  scrub: 1, // suavizado
  onUpdate: (self) => {
    const frame = Math.floor(self.progress * totalFrames);
    // Cargar frame actual
    loadFrame(frame);
    // O animar producto 3D según progreso
    updateProduct3D(self.progress);
  }
});
```

### Alternativa: Producto 3D animado con GSAP

En lugar de frames, se puede animar directamente el modelo 3D:

```js
// Descomponer el producto en 6 grupos 3D
// Cada grupo = una capa del despiece
const layers = [carcasa, leds, antena, cerebro, sensores, bateria];

const tl = gsap.timeline({
  scrollTrigger: {
    trigger: '#vscroll',
    start: 'top top',
    end: '+=600%',
    pin: true,
    scrub: 1
  }
});

// Cada capa se separa en un punto del scroll
layers.forEach((layer, i) => {
  tl.to(layer.position, {
    y: -2 - i * 0.8, // separación vertical
    opacity: 1,
    duration: 0.5
  }, i * 0.5);
});
```

### Lo que necesitas para implementar esto:

1. **Modelo 3D del ARES** (generado con ComfyUI Hunyuan3D)
2. **Separar el modelo en capas** (carcasa, LEDs, antena, cerebro, sensores, batería)
3. **Three.js + GSAP ScrollTrigger** con pin y scrub
4. **Lenis** para smooth scroll

---

## 3. Repositorio de referencia (HIVE-MIND)

En la carpeta de fichas V10 hay 18 sitios con GSAP. Los más relevantes para esta técnica:

- **getquoti.ai**: Producto SaaS con horizontal pinned scroll + animación de cards
- **slush.app**: Producto crypto con Lenis + GSAP + custom cursor + page transitions
- **rpacomunicacion.com**: 236 tweens GSAP, la referencia más compleja

---

## 4. Pick4Design Expositor

El expositor está en: `landing/expositor.html`

Muestra:
- Vista previa de la landing page (iframe)
- Colores y tipografía del proyecto
- Assets disponibles
- Lo que falta por definir
- Enlaces a todos los documentos
