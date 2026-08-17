# 03_GUIA_FABRICACION_PCB.md
**Versión:** 4.0 | **Estado:** Final | **Audiencia:** Diseñador de PCB, Fábrica (ej. JLCPCB)

---
## 1. Propósito de este Documento
*Este documento es la **guía maestra para el diseño, fabricación y ensamblaje del PCB** de ARES v4.0. Consolida todas las reglas de diseño (DRC), estándares de la industria (IPC), y los requisitos de los archivos de fabricación para asegurar un proceso de producción sin errores.*

---
## 2. Entregables para Fabricación y Ensamblaje

*Extraído de `Requisitos_Diseno_Hardware.md`*

La siguiente tabla detalla todos los archivos que se deben generar para la fabricación del PCB y el ensamblaje de componentes (PCBA).

| Entregable | Formato típico | Qué contiene | Para qué sirve | Referencia |
|---|---|---|---|---|
| **Proyecto EDA (fuente)** | KiCad/Altium/Eagle | Esquema + PCB + librerías | “Mapa” real del producto | — |
| **Gerbers** | `.gbr` | Cobre, máscara, serigrafía, contornos | Fabricación PCB | [Guía JLCPCB KiCad][1] |
| **Drill** | `.drl` + drill map | Taladros/vías | Fabricación PCB | [Guía JLCPCB KiCad][1] |
| **BOM (ensamblaje)**| `.csv/.xls/.xlsx`| Lista de componentes, valores, referencias | Compra/ensamblaje SMT | [Guía Ficheros PCBA JLCPCB][2] |
| **Pick&Place / CPL**| `.csv/.xls/.xlsx`| RefDes + centroid X/Y + capa + rotación | Máquina de colocación SMT | [Fichero Pick&Place JLCPCB][3] |
| **Drawings de ensamblaje**| PDF/PNG | Vista TOP/BOT con refs | Reduce errores de montaje | — |
| **Notas de fabricación** | PDF/TXT | Stackup, cobre (oz), máscara, impedancias | Evita “suposiciones” de la fábrica | — |
| **Stencil** | pedido o gerber de pasta | Aperturas de pasta | Depositar estaño correcto | — |
| **Plan de test (factory)**| PDF | qué medir y cómo | Garantizar que “sale vivo” | — |

---
## 3. Reglas de Diseño para el PCB de ARES v4.0

*Extraído y consolidado de `Normas diseño placa.txt`*

Estas son las reglas prácticas y estándares a seguir para el diseño del PCB de ARES, que es una placa compacta con RF (GNSS/LTE), un microcontrolador y un circuito de carga.

### 3.1. Stackup Recomendado
*   **4 capas** como base para un buen rendimiento EMC y de RF:
    *   **L1 (Top):** Componentes + Señales cortas + *Ground pour* (con stitching vias).
    *   **L2:** **Plano de GND sólido e ininterrumpido**, especialmente bajo las líneas de RF y señales rápidas.
    *   **L3:** Planos de alimentación (Power: VBAT/3V3) + señales secundarias.
    *   **L4 (Bottom):** Señales de baja velocidad + Ground pour.

### 3.2. Diseño de Alimentación (Power)
*   **Dimensionado de Pistas:** Usar el estándar **IPC-2152** para calcular el ancho de pista según la corriente y el aumento de temperatura deseado.
*   **Pulsos de Corriente (Módem):** Para las ráfagas de consumo del módem, la prioridad es una **impedancia baja**. Usar polígonos o planos anchos para VBAT y GND, múltiples vías entre capas y condensadores de desacoplo lo más cerca posible de los pines de alimentación del módem.

### 3.3. Plano de Tierra y Retornos (Regla #1 de EMC)
*   **Evitar Splits:** Nunca cortar el plano de tierra (L2) bajo una señal de alta velocidad. Una ranura obliga a la corriente de retorno a tomar un camino más largo, creando un bucle que actúa como una antena.
*   **Retorno Adyacente:** Siempre que sea posible, enrutar las corrientes de retorno en una capa adyacente directamente debajo de la pista de la señal para minimizar el área del bucle.

### 3.4. Diseño de RF (LTE/GNSS)
*   **Prioridad a la Antena:** El diseño debe empezar por la ubicación de la antena y su **zona de exclusión (keep-out)**. No se deben colocar componentes ni planos de tierra en esta zona.
*   **Línea de Alimentación (Feedline):** Debe ser una línea de impedancia controlada de **50 Ω**. Debe ser corta, directa, y mantener una referencia continua en el plano de tierra (L2).
*   **Aislamiento:** Usar "via fence" (una cortina de vías a GND) alrededor de la línea de RF para aislarla de otras señales.

### 3.5. Reglas Generales de Ruteo
*   **Ángulos de 90°:** Evitarlos en señales de alta frecuencia. Usar ángulos de 45° o arcos para prevenir reflexiones y discontinuidades de impedancia.
*   **Pistas Paralelas:** Minimizar la longitud en la que dos pistas de alta velocidad corren en paralelo para reducir el acoplamiento (crosstalk).

### 3.6. Reglas DFM (Design for Manufacturing)
*   **Footprints:** Usar patrones de huella (land patterns) estandarizados según **IPC-7351** para asegurar un buen ensamblaje y evitar problemas de soldadura.
*   **Capacidades del Fabricante (Referencia JLCPCB):**
| Caso | Ancho/espacio mínimo de pista |
|---|---|
| 1 oz, 2 capas | **0.10 / 0.10 mm** (≈4/4 mil) |
| 1 oz, multilayer | **0.09 / 0.09 mm** (≈3.5/3.5 mil) |
| 2 oz, 2 capas | **0.16 / 0.16 mm** |
| 2 oz, multilayer | **0.16 / 0.20 mm** |

---
## 4. Estándares y Referencias

*   **Dimensionado de Pistas (Corriente):**
    *   **IPC-2152:** [The ANSI Blog - IPC-2152](https://blog.ansi.org/ansi/ipc-2152-current-carrying-capacity-in-pcbs/)
*   **Espaciado Eléctrico (Clearance/Creepage):**
    *   **IPC-2221C (Tabla 6-1):** [Siemens Blog - PCB high voltage spacing](https://blogs.sw.siemens.com/electronic-systems-design/2025/04/29/pcb-high-voltage-spacing-what-every-engineer-should-know/)
    *   **IEC 60664-1:** [IEC Webstore - IEC 60664-1:2020](https://webstore.iec.ch/en/publication/59671)
*   **Diseño para EMC/EMI:**
    *   **TI - PCB Design Guidelines for Reduced EMI:** [PDF de Texas Instruments](https://www.ti.com/lit/pdf/szza009)
    *   **TI - High Speed Layout Guidelines:** [PDF de Texas Instruments](https://www.ti.com/lit/pdf/scaa082)
*   **Footprints de Componentes:**
    *   **IPC-7351:** [IPC-7351 Standard](https://www.electronics.org/TOC/IPC-7351.pdf)
*   **Diseño de Antenas:**
    *   **NordicSemi - nRF9160 Hardware Design Guidelines:** [Guía de Nordic Semiconductor](https://docs.nordicsemi.com/bundle/nwp_037/page/WP/nwp_037/nwp_037_intro.html)


[1]: https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-8
[2]: https://jlcpcb.com/help/catalog/190-PCBA-Files-Preparation
[3]: https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly
