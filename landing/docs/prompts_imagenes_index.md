# PROMPTS — Imágenes Index (ARES GPS Landing)

Modelo objetivo: Flux 2 [klein] 4B · Resolución: 1216×832 · Steps: 4 · CFG: 1.0
Generar 4 variantes por prompt, elegir la mejor. Exportar .webp calidad 85%.

---

## IMAGEN 1 — PAS Bloque: "El silencio de después de llamarlo"

### Texto que la acompaña (lado izquierdo)
> «Llamas a tu perro. Silencio. Esa fracción de segundo donde el pecho se te encoge.»
> «Con ARES abres la app. Está a 23 metros. Detrás del seto. Tú sigues andando, él sigue oliendo.»

### POV
El espectador está DE PIE al aire libre, no escondido. A unos 15-20 metros por delante hay una barrera densa de arbustos y matorrales que cruza el encuadre. Detrás de esos arbustos, parcialmente visible a través de los huecos entre las ramas y hojas, se ve a un golden retriever olisqueando el suelo. No se ve entero — la vegetación oculta sus patas y parte del cuerpo. La persona no está agachada ni escondida: está simplemente parada a cierta distancia, y sin ARES no podría saber que su perro está justo ahí, detrás de esa masa vegetal.

### Prompt — English (Flux 2 Klein)

A person's point of view standing upright in an open grassy area of an autumn park at golden hour, looking forward at a dense natural hedge and shrub line about fifteen meters ahead. The viewer is NOT hidden in the bushes — they are outside, in the open, at normal standing height, the foreground is clear grass. Behind and partially through the gaps in this thick shrubbery barrier, a golden retriever is barely visible — only its head, neck and upper shoulders peek through the foliage. The dog is on the other side of the bushes, calmly sniffing the ground, completely unaware it is being watched. The shrubs form a natural screen that hides most of the dog's body. Warm low sunset light illuminates the dog through the leaves while the foreground remains in slightly cooler shadow. In the extreme foreground bottom corner, completely out of focus, the edge of a smartphone screen glows faintly with a dark map showing a blue dot — the ARES app confirming the dog's location. The emotional message is not fear or hiding — it is the quiet miracle of knowing exactly where your dog is, even when your own eyes cannot see it. 50mm lens, f/4 for medium depth of field, photorealistic, cinematic, natural light.

Negative: crouching, hiding, person visible, dog fully visible, wide landscape, night, rain, fear, dog looking at camera, clear unobstructed view of the dog, person inside bushes, spy viewpoint, binoculars.

### Post-procesado
- Recorte: mantener al perro como foco en el centro-derecha del encuadre
- Ajuste: calidez +3%, contraste +8%
- CSS: `object-fit:cover; object-position:center`
- Formato: 1200×675px, .webp, calidad 85%
- Destino: `assets/img/pas-miedo.webp`

---

## IMAGEN 2 — PAS Bloque: "Lo que no se ve a simple vista"

### Estado
✅ IMPLEMENTADA — `assets/img/pas-salud.png` (archivo original en Downloads)

### Texto que la acompaña
> «¿Ha corrido hoy lo que necesita? ¿Ha descansado bien esta noche? Nunca lo sabes del todo.»
> «Con ARES lo sabes al momento: actividad, descanso, frecuencia respiratoria en reposo. No adivinas: sabes.»

### Concepto (para referencia)
División diagonal a 45° desde abajo-izquierda a arriba-derecha. Triángulo superior: border collie + galgo + bulldog francés jugando en prado soleado, cada uno en pose distinta y natural. Triángulo inferior: perra mastín del pirineo durmiendo boca arriba sobre alfombra con un juguete mordido al lado. Collar ARES visible en ambos lados. La diagonal no es una línea dura — es un degradado suave donde el pasto se funde con la alfombra.

### HTML
```html
<div class="pas-img">
  <div class="ph-bg"><img src="assets/img/pas-salud.png" alt="Perros jugando y perra durmiendo" class="ph-img"></div>
</div>
```

### CSS
```css
.ph-img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
```

---

## NOTA
La Imagen 2 ya está puesta en producción (index.html línea 461). La Imagen 1 se generará con Flux 2 Klein y se insertará en el primer bloque PAS (línea 448-450).
