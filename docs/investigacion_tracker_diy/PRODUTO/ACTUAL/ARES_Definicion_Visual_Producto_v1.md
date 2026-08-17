# ARES — Definición Visual del Producto v8.2 (FINAL)

## Fecha: 2026-08-08 | Listo para render

> **Cambio v8.0 → v8.1:** el remate de las Ls LED deja de ser "punta fina progresiva de 5mm"
> y pasa a ser un **corte limpio en bisel a 45°**. El tramo largo cubre **exactamente 3/4** del
> lateral, dejando el **último 1/4 como plástico verde militar continuo sin luz**. Ver §2.2.
>
> **Cambio v8.1 → v8.2 (2026-08-13):** añadida **§2.4 Visibilidad de la luz — cobertura angular**
> (la L trasera debe verse desde ángulos posteriores y laterales a la vez; la ventana debe quedar
> al ras, no rehundida). Imagen de referencia del dispositivo: `referencias/dispositivo_referencia_2026-08-13.png`.


## 1. MEDIDAS

63mm largo × 41mm ancho × 21mm grosor. Paredes 3mm ABS/PC verde militar (`#5C6B3C`).


## 2. LEDs — LAS Ls

### 2.1 Posición (CORREGIDA)

2 Ls en esquinas diagonales opuestas:

| | Esquina | Tramo corto | Tramo largo |
|---|---------|:---:|:---:|
| **L1 ┐** | Superior-izquierda | **1/2** del borde superior | **3/4** del borde izquierdo |
| **L2 ┘** | Inferior-derecha | **1/2** del borde inferior | **3/4** del borde derecho |

- Esquina **superior-derecha: SIN luz**
- Esquina **inferior-izquierda: SIN luz**
- Solo 2/4 esquinas tienen LEDs

### 2.2 Terminación del extremo — CORTE LIMPIO A 45° (v8.1)

El extremo final del LED **no se estrecha en punta fina**; termina en un **corte limpio en bisel a 45°**. El tramo de la L mantiene su **~1cm de ancho constante** en TODO su recorrido, incluido el extremo — el ancho no disminuye. El LED simplemente **se interrumpe de golpe** con un corte recto en diagonal (45°).

**Proporción del tramo largo (confirmada):** el tramo largo de la L cubre **exactamente 3/4 del lateral largo** y se interrumpe ahí. El **1/4 restante** del bisel queda como **plástico verde militar continuo sin luz** (mismo `#5C6B3C` que el resto de la carcasa).

- [NO]  NO hay punta fina ni estrechamiento progresivo
- [NO]  NO desaparece en un punto
- [OK]  Ancho constante de ~1cm hasta el final
- [OK]  Corte brusco y recto a 45° en el extremo
- [OK]  Último 1/4 del lateral = plástico verde sin luz, continuo

### 2.3 Ventana de policarbonato + micro O-ring

Cada L tiene una ventana de policarbonato cristal de 2mm de grosor con la cara exterior frosted. Se inserta a presión en el hueco del chaflán 45°.

**Montaje del micro O-ring:**
1. El hueco del chaflán tiene una **ranura perimetral** en su borde interior
2. Colocar micro O-ring de silicona (Ø0.5mm) en dicha ranura
3. Presionar la ventana PC hasta que quede **al ras** (flush) con la superficie del chaflán
4. La ventana comprime el O-ring contra las paredes de la ranura → sello IP68

### 2.4 Visibilidad de la luz — cobertura angular (CORREGIDO 2026-08-13)

> Aclaración del usuario con la imagen de referencia (`referencias/dispositivo_referencia_2026-08-13.png`): la luz **no debe quedar escondida** en ningún ángulo de visión habitual del usuario.

**Requisito:** cada L debe ser claramente visible **simultáneamente desde los ángulos posteriores y laterales** del dispositivo (el dueño mira al perro de frente, de lado y desde atrás).

- **Cobertura del bisel:** la ventana de la L cubre el tramo indicado en §2.1 (**1/2** en el tramo corto, **3/4** en el tramo largo) y **NUNCA debe acortarse más** que esas proporciones. El corte limpio a 45° es el final del tramo LUMINOSO, no un lugar donde la luz se atenúa o desaparece gradualmente.
- **Proyección desde el chaflán:** al estar la L sobre el bisel a 45° (no en la cara plana), la luz se proyecta en diagonal — debe seguir llegando a los **lados (laterales) y a la parte trasera** a la vez. El difusor frosted debe repartir la luz en el plano del chaflán sin crear un "punto caliente" que solo se vea desde un ángulo.
- **Ángulos de control (para verificar en render):** la L trasera (L2 ┘, esquina inferior-derecha) debe verse desde:
  - Vista trasera (el dueño detrás del perro): se ve el tramo largo derecho.
  - Vista lateral derecha: se ve el tramo largo.
  - Vista 3/4 trasera-derecha (la más crítica): se ve la L completa sin que la esquina la oculte.
- [NO]  La ventana **no debe quedar rehundida** respecto al chaflán (si queda hundida, la pared proyecta sombra y apaga la luz lateralmente). Debe quedar **al ras (flush)**, como indica §2.3 paso 3.
- [NO]  Ningún refuerzo interno, tornillo, poste o reborde de la columna debe tapar la ventana de la L trasera desde el lateral.


## 3. CAVIDADES — 4 COLUMNAS DE ESQUINA

### 3.1 Dónde están

4 cavidades, una en cada **columna de esquina** (la cara de 21mm de grosor que une la cara superior con la inferior).

### 3.2 Qué NO son

- [NO]  NO son agujeros pasantes (no atraviesan la columna)
- [NO]  NO tienen forma de flecha dibujada/cincelada
- [NO]  NO hay una flecha visible desde fuera

### 3.3 Qué SÍ son

Una **cavidad cerrada** mecanizada dentro de la columna, con las siguientes partes:

```
   COLUMNA (vista frontal de la cara de 21mm):

   ┌──────────────────────────────┐
   │                              │
   │   ┌──────────────────────┐   │  ← entrada (la goma se
   │   │                      │   │     mete por aquí)
   │   │     CAVIDAD          │   │
   │   │     (hueco hacia     │   │  ← rebaje dentro de la
   │   │      dentro del      │   │     columna, NO traspasa
   │   │      plástico)       │   │
   │   │                      │   │
   │   │   ┌──────┐           │   │
   │   │   │DIENTE│           │   │  ← resalte que queda
   │   │   │(lo que│           │   │     DENTRO de la cavidad.
   │   │   │queda │           │   │     Es parte del plástico
   │   │   │de la  │           │   │     NO eliminado.
   │   │   │mecani│           │   │
   │   │   │zación│           │   │
   │   │   └──┬───┘           │   │
   │   │      │               │   │  ← salida de la goma
   │   └──────┼───────────────┘   │     hacia abajo (collar)
   │          │                   │
   └──────────┼───────────────────┘
              │
              ▼  al collar
```

**El "diente" o "flecha" NO está dibujado.** Es el material que QUEDA después de vaciar la cavidad — la propia geometría del plástico crea un resalte que atrapa la goma.

### 3.4 Cómo funciona

1. La goma entra por la abertura superior de la cavidad
2. Pasa por debajo del diente/resalte interno
3. Se aloja en el fondo
4. Cuando el perro tira (↓), la goma empuja contra el diente
5. El diente **impide que suba** (está tapado por arriba)
6. Para soltar: empujar hacia arriba (↑) manualmente y luego sacar

### 3.5 Dimensiones

| Parámetro | Medida |
|-----------|:------:|
| Altura total cavidad | ~12mm |
| Profundidad (hacia dentro) | 8mm |
| Ancho entrada | 4mm |
| Altura diente | 2mm |
| Hueco NO es pasante | [OK]  — fondo cerrado |

### 3.6 Para el render

- La goma **NO se ve** en la imagen
- Solo se ve la cavidad (el hueco con el resalte interno)


## 4. TEXTURA Y ACABADO

| Zona | Acabado |
|------|---------|
| **Cara SUPERIOR** | Textura geométrica (Y-shape interlocking / colmena hexagonal) |
| **Logo ARES** | Grabado en la cara superior |
| **Laterales bajo chaflán** | **LISOS** (sin textura) |
| **Esquinas** | **REDONDEADAS** (radio ~3-4mm) |
| **Chaflán 45°** | Ventanas PC frosted insertadas |


## 5. RESUMEN DE CARAS

| Cara | Qué lleva |
|------|-----------|
| SUPERIOR | **Logo = X simple** (no letras) + textura geométrica |
| CHAFLÁN 45° | Las 2 Ls están AQUÍ, en el bisel inclinado. L1 ┐ sup-izq (corto 1/2 arriba + largo 3/4 izquierda). L2 ┘ inf-der (corto 1/2 abajo + largo 3/4 derecha). Esquinas sup-der e inf-izq SIN luz |
| COLUMNAS (×4) | 1 cavidad por columna (rectangular, con diente interno) |
| LATERALES | LISOS. Esquinas redondeadas |
| INFERIOR | Pogo magnético + LED carga |


## 6. PROMPTS FINALES

### Prompt 1 — Vista isométrica

> ARES GPS dog tracker 63x41x21mm, rectangular, rounded corners, dark olive green ABS/PC. The top face has geometric texture and a simple engraved X icon (no letters, no text, just an X). The 45-degree chamfered edges around the perimeter contain TWO L-shaped glowing strips made of clear frosted polycarbonate. L1 at top-left corner: short leg runs 1/2 way across the top chamfer, long leg runs 3/4 down the left chamfer. L2 at bottom-right corner: short leg runs 1/2 across the bottom chamfer, long leg runs 3/4 up the right chamfer. The Ls are ON the 45-degree beveled surface itself, not on the flat top face. The LED strip is a constant 1cm wide along its entire length and does NOT taper; it ends abruptly in a clean 45-degree beveled cut, not a fine point. The long leg covers exactly 3/4 of the side edge and stops there, leaving the remaining 1/4 of the chamfer as continuous unlit olive-green plastic. Top-right and bottom-left corners have no LED. The side faces below the chamfer are smooth, not textured. On each corner column (the 21mm deep side edges) there is a rectangular recessed slot with an internal retaining tooth visible. Rubber not shown. Black background, studio lighting, photorealistic 8K product shot.

### Prompt 2 — Detalle LED en el chaflán

> Macro close-up of the 45-degree chamfered edge of the ARES GPS tracker. The L-shaped LED strip runs exactly on this angled bevel surface, not on the flat top or side. Clear frosted polycarbonate window flush with the chamfer. Constant 1cm width glowing cyan-white along its entire length, ending in a clean 45-degree beveled cut — it does NOT taper to a point. The lit strip covers 3/4 of the edge and stops abruptly, the final 1/4 of the chamfer is continuous unlit olive-green plastic. The textured top face is visible above the chamfer, the smooth side face is below. Olive green ABS/PC. Black background, 8K macro.

### Prompt 3 — Detalle cavidad columna

> Macro close-up of the corner of an ARES GPS tracker. On the 21mm deep side face of the corner column, there is a rectangular recessed slot with an internal protruding ledge visible inside. The cavity is not a through-hole. The slot has a closed top and an internal tooth retaining ledge. Rounded corner. Smooth side surface. Above it the 45-degree chamfer with frosted LED window. Olive green ABS/PC. Black background, dramatic lighting, 8K.


## 7. HERRAMIENTAS WEB

| Herramienta | Tipo | URL |
|-------------|------|-----|
| Meshy.ai | Texto → 3D | meshy.ai |
| Luma AI Genie | Texto → 3D | lumalabs.ai/genie |
| ComfyUI Cloud | Texto → imagen 2D | comfy.org |
| Spline | Visualizar 3D | spline.design |
| Blender | CAD + render | blender.org |


## 8. DOCUMENTOS

| Archivo | Qué es |
|---------|--------|
| `ARES_Definicion_Visual_Producto_v1.md` | Este documento v8.0 |
| `ARES_Despiece_Montaje_v1.md` | Despiece, montaje, IP68, secuencia explodida |
