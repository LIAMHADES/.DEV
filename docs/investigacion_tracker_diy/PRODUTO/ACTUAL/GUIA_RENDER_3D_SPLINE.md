# ARES — Guía para crear el modelo 3D en SPLINE (web gratis)

## Herramienta: [spline.design](https://spline.design) (gratis, web, sin instalar)

---

## PASO 1 — Crear la caja base

1. Abrir spline.design → New file
2. Menú derecho → Add → Box
3. En el panel derecho, poner dimensiones exactas:
   - Width (X): **63mm**
   - Height (Y): **21mm** 
   - Depth (Z): **41mm**
4. Renombrar a "Cuerpo principal"

---

## PASO 2 — Redondear esquinas

1. Seleccionar el cubo
2. En el panel de propiedades, buscar "Corner Radius"
3. Poner **3mm** (todas las esquinas se redondean)
4. Esto crea el perfil redondeado del ARES

---

## PASO 3 — Crear el chaflán de 45° para los LEDs

1. Add → Lathe (o usar un prisma triangular)
2. Crear un perfil triangular de 45° con las medidas:
   - Base: ~5mm
   - Altura: ~5mm  
3. Duplicar y alargar para formar cada L:
   - **L1 (superior-izquierda):** 
     - Tramo corto: de la esquina superior-izquierda hasta la mitad del borde superior (~20mm)
     - Tramo largo: de la esquina superior-izquierda hasta 3/4 del borde izquierdo (~47mm)
   - **L2 (inferior-derecha):**
     - Tramo corto: de la esquina inferior-derecha hasta la mitad del borde inferior (~20mm)
     - Tramo largo: de la esquina inferior-derecha hasta 3/4 del borde derecho (~47mm)
4. Material de este chaflán: **Frosted glass** o **Translucent plastic**

---

## PASO 4 — LEDs

1. Dentro del chaflán, añadir cilindros aplanados (0.5mm grosor)
2. Colocar **6 LEDs por L** (12 total), espaciados ~10mm
3. Material: **Emissive** → color cian/azul (`#00E5FF`), intensidad 2-3

---

## PASO 5 — Cavidades para las gomas en columnas

1. Add → Box (pequeño), poner dimensiones: 4mm × 8mm × 6mm
2. Colocar en la cara frontal de UNA columna de esquina (cara de 21mm de grosor)
3. Usar **Boolean → Subtract** para restar la cavidad del cuerpo principal
4. Repetir en las 4 columnas de esquina

---

## PASO 6 — Logo X

1. Add → Text, escribir "X"
2. Fuente: sans-serif bold
3. Colocar centrado en la cara superior
4. Extruir 0.5mm (relieve) o usar Boolean Subtract para grabado

---

## PASO 7 — Textura superior

1. Seleccionar la cara superior del cuerpo
2. Material: agregar patrón geométrico (hexagonal o Y-shape)
3. Color: verde militar oscuro `#5C6B3C`
4. Las caras laterales: mismo material pero sin textura (lisas)

---

## PASO 8 — Render final

1. Añadir fondo negro (Scene → Background → Solid → Black)
2. Iluminación: Studio (3 puntos de luz)
3. Cámara: isométrica (ángulo 30°)
4. Exportar: PNG 4K

---

## ALTERNATIVA: MESHY.AI (más rápido, IA)

Si prefieres IA en vez de modelar manual:

1. Ir a [meshy.ai](https://meshy.ai)
2. Registrarse (200 créditos gratis)
3. **Text to 3D** → pegar este prompt:

> GPS dog tracker 63x41x21mm rectangular device, dark olive green, rounded corners, two L-shaped LED strips on opposite diagonal corners, L1 top-left (short on top 1/2, long on left 3/4), L2 bottom-right (short on bottom 1/2, long on right 3/4), X logo engraved on top, four corner columns with slot cavities on the 21mm side edges, smooth sides below chamfer

4. Descargar el .glb
5. Opcional: abrirlo en Spline para ajustar y renderizar
