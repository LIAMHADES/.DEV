# ARES — Despiece, Montaje y Verificación IP68 v3.0

## Fecha: 2026-07-22 | Diseño unificado + ventanas insertadas + cavidades laterales


## 1. DECISIONES DE DISEÑO

| # | Decisión | Motivo |
|---|----------|--------|
| 1 | **Carcasa unificada** | 1 junta IP68 en vez de 2. Menos piezas. Más barato |
| 2 | **Lámina de grafito 0.5mm** entre chip y batería | Barrera térmica sin separar físicamente |
| 3 | **Ventanas de policarbonato insertadas** (2mm) en chaflanes | Estructura mantiene 3mm. Reemplazable si se rompe |
| 4 | **2 cavidades flecha ↑ en medio de lados largos** | Goma entra desde abajo. Tira hacia abajo = se clava más |
| 5 | **Tornillos M2 acero inox + O-ring individual** | Presión uniforme sobre la junta. Escalable |
| 6 | **Ls de LEDs terminan en CORTE LIMPIO a 45°** (v8.1, antes "en punta") | Ancho constante ~1cm; el LED se interrumpe de golpe con corte recto a 45°. El tramo largo cubre 3/4 del lateral, el 1/4 restante queda como plástico verde sin luz. Ver `ARES_Definicion_Visual_Producto_v1.md` §2.2 |


## 2. LISTA DE PIEZAS (6 piezas)

| # | Pieza | Material | Cant | Quién lo hace |
|---|-------|----------|:---:|---------------|
| 1 | **Carcasa superior** | ABS/PC verde militar | 1 | JLC3DP (SLA) |
| 2 | **Carcasa inferior** | ABS/PC verde militar | 1 | JLC3DP (SLA) |
| 3 | **PCB + batería** (pre-conectados JST) | FR4 + LiPo 123450 | 1 | JLCPCB (PCBA) + proveedor batería |
| 4 | **Ventanas LED** (2 uds, forma L, 2mm) | Policarbonato cristal | 2 | JLC3DP (SLA clear resin) |
| 5 | **Micro O-rings ventanas** (Ø0.5mm) | Silicona | 2 | Proveedor estándar |
| 6 | **Kit sellado** | O-ring silicona Ø2mm + 4 tornillos M2 inox A2 + 4 O-ring tornillo | 1 | Proveedor estándar |


## 3. PREGUNTA CLAVE: ¿QUIÉN ENSAMBLA QUÉ?

| Fase | Quién | Qué hace |
|------|-------|----------|
| **A** | JLCPCB | Suelda TODOS los componentes SMD en la PCB (LilyGo, BMI270, Ignion, LEDs, MOSFETs, resistencias) |
| **B** | Proveedor batería | Suelda BMS (BQ24040 + NTC + protección) a la celda LiPo. Suelda cable JST macho |
| **C** | JLC3DP | Imprime carcasa superior, carcasa inferior, 2 ventanas LED |
| **D** | **TÚ o taller local** | Ensamblaje final: mete batería en carcasa inferior, conecta JST a PCB, coloca grafito, inserta ventanas con micro O-ring, coloca O-ring perimetral, cierra, atornilla |
| **E** | **TÚ** | Test de inmersión IP68 |

> Ni JLCPCB ni JLC3DP hacen ensamblaje mecánico completo. La fase D la haces tú para prototipos. Para producción en masa, contratas un taller de ensamblaje en España o Portugal. Coste estimado: ~3-5€/unidad para series de 100+.


## 4. MONTAJE PASO A PASO (5 pasos + verificación)

```
   ┌─────────────────────────────────────────────────────────┐
   │  PASO 1: Batería + conector carga en carcasa inferior   │
   │                                                         │
   │  • Batería 123450 (con BMS, NTC, BQ24040 ya soldados)  │
   │    se coloca en su hueco en la carcasa inferior.        │
   │  • Pads de espuma adhesiva (2mm) en los laterales       │
   │    fijan la batería sin movimiento.                     │
   │  • Conector magnético se encaja a presión en su         │
   │    cavidad de la cara inferior (IP68 mated).            │
   │  • Cable JST de la batería queda libre hacia arriba.    │
   │                                                         │
   │  [ATENCION]  ERROR POSIBLE: batería mal centrada → no cierra.    │
   │  [OK]  SOLUCIÓN: guías de alineación en el hueco.          │
   └─────────────────────────────────────────────────────────┘
                            ↓
   ┌─────────────────────────────────────────────────────────┐
   │  PASO 2: Conectar PCB + colocar grafito                 │
   │                                                         │
   │  • Conectar cable JST de batería a conector JST hembra  │
   │    en la PCB. (1 solo conector, 2 pines, imposible      │
   │    conectarlo al revés).                                │
   │  • Colocar lámina de grafito 0.5mm entre PCB y batería. │
   │    El grafito se fija con 2 puntos de cinta adhesiva.   │
   │  • Thermal pad de 1mm entre SIM7000G y punto de         │
   │    contacto con la tapa superior.                       │
   │                                                         │
   │  [ATENCION]  ERROR POSIBLE: grafito toca pines → cortocircuito.  │
   │  [OK]  SOLUCIÓN: grafito recortado 2mm más pequeño que     │
   │     la huella de la batería. No toca bordes de PCB.     │
   └─────────────────────────────────────────────────────────┘
                            ↓
   ┌─────────────────────────────────────────────────────────┐
   │  PASO 3: Insertar ventanas LED en carcasa superior      │
   │                                                         │
   │  • Cada ventana (forma L) tiene un micro O-ring de      │
   │    silicona (Ø0.5mm) alrededor de su perímetro.         │
   │  • Se inserta a presión en el hueco del chaflán 45°.    │
   │  • La ventana queda FLUSH (al ras) con la superficie.   │
   │  • 2 ventanas = 2 Ls (L1 ┐ sup-izq, L2 ┘ inf-der).    │
   │                                                         │
   │  [ATENCION]  ERROR POSIBLE: micro O-ring se sale al insertar.    │
   │  [OK]  SOLUCIÓN: canal receptor con labio de retención      │
   │     de 0.3mm. Un poco de vaselina de silicona ayuda.    │
   └─────────────────────────────────────────────────────────┘
                            ↓
   ┌─────────────────────────────────────────────────────────┐
   │  PASO 4: O-ring perimetral + cerrar                     │
   │                                                         │
   │  • Colocar O-ring de silicona (Ø2mm) en el canal de     │
   │    la carcasa inferior (recorrido perimetral completo). │
   │  • Bajar la tapa superior (con PCB y ventanas ya        │
   │    montadas) sobre la inferior.                         │
   │  • Los 4 taladros de tornillo deben alinearse.          │
   │  • Insertar 4 tornillos M2 inox con sus mini O-rings.   │
   │  • Apretar en CRUZ (↗↙↘↖) — mismo principio que        │
   │    la rueda de un coche. NO apretar a tope el primero.  │
   │  • Par de apriete: ~0.3 N·m (manual, firme sin forzar). │
   │                                                         │
   │  [ATENCION]  ERROR POSIBLE: O-ring pellizcado → no sella.        │
   │  [OK]  SOLUCIÓN: inspección visual antes de cerrar.         │
   │     El canal debe ser 20% más profundo que el Ø del     │
   │     O-ring para que este se comprima, no se corte.      │
   └─────────────────────────────────────────────────────────┘
                            ↓
   ┌─────────────────────────────────────────────────────────┐
   │  PASO 5: Tests                                          │
   │                                                         │
   │  5a. Test eléctrico:                                    │
   │      • Conectar cargador magnético → LED de carga       │
   │        debe encenderse (rojo cargando).                 │
   │      • Si no enciende → abrir, revisar conexión JST.   │
   │                                                         │
   │  5b. Test de inmersión IP68 (SIN electrónica):          │
   │      • Montar carcasa VACÍA con papel secante dentro.   │
   │      • Sumergir 30 min a 1 metro de profundidad.        │
   │      • Abrir → papel debe estar COMPLETAMENTE SECO.     │
   │      • Si está húmedo → revisar O-ring (pellizcado,     │
   │        mal asentado, canal con rebaba).                 │
   │      • Si está seco → [OK]  IP68 VERIFICADO.               │
   │                                                         │
   │  5c. Montar con electrónica y repetir test.             │
   │                                                         │
   │  [ATENCION]  ERROR POSIBLE: test sin electrónica OK pero con     │
   │     electrónica falla → el cable JST o el conector      │
   │     de carga crean un punto de entrada.                 │
   │  [OK]  SOLUCIÓN: el conector de carga es IP68 mated por     │
   │     especificación. El JST va dentro, sin exposición.   │
   └─────────────────────────────────────────────────────────┘
```


## 5. VERIFICACIÓN IP68 — CHECKLIST

| Punto de entrada potencial | ¿Sellado? | Cómo |
|----------------------------|:---:|------|
| Junta entre tapas | [OK]  | O-ring silicona Ø2mm en canal perimetral |
| Ventanas LED (2) | [OK]  | Micro O-ring Ø0.5mm alrededor de cada ventana |
| Tornillos (4) | [OK]  | Mini O-ring bajo cada cabeza de tornillo |
| Conector carga magnética | [OK]  | IP68 mated por especificación (pogo pins sellados) |
| Cable JST batería↔PCB | [OK]  | Va DENTRO de la carcasa sellada, sin exposición |
| Logo grabado | [OK]  | Grabado superficial (0.1mm), no atraviesa la pared |
| Textura geométrica | [OK]  | Relieve externo, no atraviesa |


## 6. SECUENCIA ANIMACIÓN EXPLODIDA

| Frame | Qué se mueve | Dirección |
|:-----:|-------------|:---------:|
| 1 | **4 tornillos** se desenroscan de la cara inferior | ↓ abajo |
| 2 | **Carcasa superior** se eleva | ↑ arriba |
| 3 | **2 ventanas LED** (forma L) se separan de los chaflanes | ←→ laterales |
| 4 | **PCB** se extrae (cable JST se desconecta) | ↑ arriba |
| 5 | **Lámina de grafito** se separa | ↑ arriba |
| 6 | **Batería** se extrae de la carcasa inferior | ↑ arriba |
| 7 | **Conector carga magnética** se desencaja de la cara inferior | ↓ abajo |
| 8 | **O-ring perimetral** se retira del canal | ↑ arriba |
| 9 | Plano general con las 6 piezas + accesorios flotando | - |
| 10 | **Reverso:** montaje (piezas vuelven a su sitio) | ↓ |
| 11 | **Cierre final:** logo ARES visible, LEDs se iluminan (cyan) | - |


## 7. ¿IP68 CON PIEZAS IMPRESAS EN 3D?

| Factor | ¿Problema? | Solución |
|--------|:---:|----------|
| Porosidad de la resina SLA | [ATENCION]  Microporos en la superficie | Lijar canal del O-ring con lija 800 → superficie lisa |
| Tolerancias de impresión (±0.1mm) | [ATENCION]  Puede afectar el ajuste del O-ring | Usar O-ring de Ø2mm (20% más grueso) para compensar |
| Snap-fits / clips | [NO]  No se usan. Tornillos dan presión uniforme | [OK]  |
| Ventanas insertadas | [ATENCION]  Micro O-ring delicado | Test individual de cada ventana antes de montaje |
| Paso del tiempo | [ATENCION]  La resina SLA puede degradarse con UV | Pintar o lacar la carcasa con protector UV |
| Producción en molde | [OK]  Sin problemas | El molde de inyección da superficies perfectas |


## 8. COMPARATIVA FINAL

| | v1 (modular) | v2.1 (unificado + ventanas) |
|---|:---:|:---:|
| Piezas | 7 | **6** |
| Juntas IP68 | 2 grandes | **1 grande + 2 micro + 4 mini-tornillo** |
| Puntos de entrada de agua | 4+ | **7 (todos sellados)** |
| Fallo de junta = tracker muerto | [OK]  (doble junta) | [OK]  (una junta, pero más simple = menos riesgo) |
| Montaje | 7 pasos | **5 pasos** |
| Herramientas | Destornillador + llave | **Llave Allen 2mm** |
| Escalable | [OK]  | [OK]  |

