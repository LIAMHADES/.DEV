## Tabla 1 — Módulo batería (BOM funcional mínima, 1S LiPo)

| Bloque                             | Componentes (qué necesitas en el módulo batería)             | Parámetros que hay que definir                           | Notas                                                    |
| ---------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------- | -------------------------------------------------------- |
| Celda                              | Batería LiPo/Li-ion **1S**                                   | Capacidad (mAh), tamaño (L×W×T), C-rate, con/sin NTC     | Nominal 3.7 V, 4.2 V a carga completa (típico 1S).       |
| Protección (BMS)                   | Protector 1S (OVP/UVP/OCP) si la celda no lo trae            | Umbrales OVP/UVP, corriente de corte                     | En muchos packs viene integrado; si no, hay que ponerlo. |
| Medición temperatura               | **NTC** (en pack o en PCB)                                   | Valor (10k/100k), curva B, límites carga/descarga        | Necesario para cortar carga por temperatura.             |
| Carga                              | IC cargador Li-ion (lineal o switching)                      | Corriente de carga (mA), terminación, thermal regulation | Define “tiempo de carga” y disipación térmica.           |
| Entrada de carga                   | USB-C **o** pogo/magnético + protección                      | Si USB-C: ESD/TVS. Si pogo: chapado, fuerza, sellado     | La entrada define carcasa/IP y test.                     |
| Power path / protección de sistema | Load switch / ideal diode / power mux (según arquitectura)   | Prioridad carga vs sistema, caída de tensión             | Evita resets al conectar/desconectar cargador.           |
| Regulación                         | (Si va en este módulo) LDO/Buck 3.3 V, y/o rail VBAT directo | Corriente máxima, dropout/eficiencia, ruido              | Si el módem va en otro módulo, esto puede ir allí.       |
| Conexión a módulo “chip”           | Conector board-to-board / FPC / JST / pads                   | Nº pines, corriente por pin, keying, retención           | Define montaje rápido y fiabilidad.                      |
| Test/producción                    | Pads de test + identificación                                | Testpoints VBAT/GND/NTC/ID, etiqueta QR                  | Necesario para test eléctrico rápido.                    |

---

## Tabla 2 — PCB (archivos que debes **generar** para fabricar/ensamblar)

| Entregable             | Formato típico           | Qué contiene                               | Para qué sirve                                               | Referencia                                             |
| ---------------------- | ------------------------ | ------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------ |
| Proyecto EDA (fuente)  | KiCad/Altium/Eagle       | Esquema + PCB + librerías                  | “Mapa” real del producto (no se envía a fábrica normalmente) | —                                                      |
| Gerbers                | `.gbr`                   | Cobre, máscara, serigrafía, contornos      | Fabricación PCB                                              | Guía JLCPCB KiCad: capas mínimas + drill ([JLCPCB][1]) |
| Drill                  | `.drl` + drill map       | Taladros/vías                              | Fabricación PCB                                              | ([JLCPCB][1])                                          |
| BOM (ensamblaje)       | `.csv/.xls/.xlsx`        | Lista de componentes, valores, referencias | Compra/ensamblaje SMT                                        | Catálogo “PCBA Files Preparation” ([JLCPCB][2])        |
| Pick&Place / CPL       | `.csv/.xls/.xlsx`        | RefDes + centroid X/Y + capa + rotación    | Máquina de colocación SMT                                    | Campos requeridos por JLCPCB ([JLCPCB][3])             |
| Drawings de ensamblaje | PDF/PNG                  | Vista TOP/BOT con refs                     | Reduce errores de montaje                                    | —                                                      |
| Notas de fabricación   | PDF/TXT                  | Stackup, cobre (oz), máscara, impedancias  | Evita “suposiciones” de la fábrica                           | —                                                      |
| Stencil                | pedido o gerber de pasta | Aperturas de pasta                         | Depositar estaño correcto                                    | —                                                      |
| Plan de test (factory) | PDF                      | qué medir y cómo                           | Garantizar que “sale vivo”                                   | —                                                      |

---

## Tabla 3 — Reglas DFM rápidas (referencia JLCPCB; útil para tu DRC)

| Caso             | Ancho/espacio mínimo de pista (referencia) | Nota                                                       |
| ---------------- | ------------------------------------------ | ---------------------------------------------------------- |
| 1 oz, 2 capas    | **0.10 / 0.10 mm** (≈4/4 mil)              | Valores de capacidad publicados por JLCPCB ([JLCPCB][4])   |
| 1 oz, multilayer | **0.09 / 0.09 mm** (≈3.5/3.5 mil)          | JLCPCB indica 3 mil permitido en fan-out BGA ([JLCPCB][4]) |
| 2 oz, 2 capas    | **0.16 / 0.16 mm**                         | Más cobre = más difícil de grabar fino ([JLCPCB][4])       |
| 2 oz, multilayer | **0.16 / 0.20 mm**                         | ([JLCPCB][4])                                              |

---

### (Opcional) Copia rápida en “texto tipo lista” para pegar

**Módulo batería:** celda 1S + (protección si no viene) + NTC + cargador + conector carga (USB-C o pogo) + ESD/TVS + power-path/load switch (según arquitectura) + (regulación si aplica) + conector a módulo chip + pads de test/ID.

**PCB a fabricar/ensamblar:** Gerbers + drill + BOM + Pick&Place/CPL (centroid X/Y, capa, rotación) + notas stackup/cobre/impedancia + drawings + plan de test. ([JLCPCB][3])

[1]: https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-8?utm_source=chatgpt.com "How to generate Gerber and Drill files in KiCAD 8?"
[2]: https://jlcpcb.com/help/catalog/190-PCBA-Files-Preparation?utm_source=chatgpt.com "PCBA Files Preparation - JLCPCB Help Center"
[3]: https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly "Pick & Place File for PCB Assembly"
[4]: https://jlcpcb.com/blog/how-to-avoid-pitfalls-in-pcb-design?utm_source=chatgpt.com "How to Avoid Pitfalls in PCB Design"
