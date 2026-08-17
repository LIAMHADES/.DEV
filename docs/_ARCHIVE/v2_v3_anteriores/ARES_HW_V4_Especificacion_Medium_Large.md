# Cambios V2.3 — Baterías, carcasa, LEDs y carga (Medium/Large)

## 0) Alcance de este documento

* Este documento **actualiza** decisiones y parámetros para **Medium y Large**.
* **Small** queda como *side quest*: no se diseña ahora. Solo se fija que **no llevará tiras**; como mucho un **LED pequeño de estado** (a definir más adelante).
* Objetivo: que el equipo pueda **actualizar los documentos anteriores** (carcasa/PCB/energía/LEDs/carga) con una sola fuente.

---

## 1) Decisiones congeladas

### 1.1 Baterías *(Selección abierta a cambios según disponibilidad y optimización)*

* Mantener estrategia: **misma huella (ancho/largo) y escalar capacidad aumentando solo grosor**.
* Referencias elegidas (pouch LiPo 1S, 3.7 V nominal / 4.2 V full):

  * **Small (no se diseña ahora):** 603450 ~1200 mAh.
  * **Medium:** **123450 ~2700–2750 mAh**.
  * **Large:** **Pack 1S2P ~4000 mAh** manteniendo huella (típicamente comercializado como **103450 1S2P**).

### 1.2 Carcasa (módulo batería) — dimensiones internas *(Dimensiones flexibles, sujetas a la selección final de componentes)*

* A partir de **Medium**, se congela la huella interna como:

  * **W × L = 36 × 58 mm** (**paredes interiores**)
  * Motivo: asegurar compatibilidad Medium/Large (mismo “cartucho”) + margen para cables + tolerancias, incluyendo variantes que crecen en largo por PCM/cables.
* **Medium y Large compartirán la misma huella interna**. Solo cambia:

  * **Grosor (profundidad/alto)** del hueco y, por tanto, el grosor del módulo.

### 1.3 Conexión y carga

* Se elimina el concepto de “LED verde en el módulo batería” porque:

  * batería y chip estarán **normalmente conectados**,
  * se usará **carga magnética**,
  * rara vez se separará el módulo batería.
* Se prioriza **carga magnética tipo pogo** (sin USB-C expuesto).

---

## 2) Baterías: modelos, medidas y links

> Nota: en baterías pouch, el código (p.ej. 123450) suele referir a **celda**. El **pack** real puede crecer en largo/ancho por PCM, termorretráctil y salida de cables. Por eso se sobredimensiona el hueco a 36×58.

### 2.1 Small (referencia, no se diseña ahora)

* **603450 ~1200 mAh**

  * Ejemplos compra:

    * AMPUL: [https://ampul.eu/es/baterias/3177-bateria-li-pol-1200mah-37v-603450](https://ampul.eu/es/baterias/3177-bateria-li-pol-1200mah-37v-603450)
    * RobotShop EU (BricoGeek): [https://eu.robotshop.com/es/products/bricogeek-bateria-lipo-1200mah-37v-603450](https://eu.robotshop.com/es/products/bricogeek-bateria-lipo-1200mah-37v-603450)

### 2.2 Medium (se diseña)

* **123450 ~2700–2750 mAh** (misma huella, más grosor)

  * Fabricante (ejemplo): Honcell HCP123450 2750 mAh:

    * [https://www.honcell.com/lithium-battery/cells/hcp-lipo-battery-cells/2704](https://www.honcell.com/lithium-battery/cells/hcp-lipo-battery-cells/2704)
  * Ejemplo pack con PCM/cables publicado (dimensiones “pack”):

    * [https://www.lithiumlifepo4battery.com/quality-13776872-3-7v-2750mah-rechargeable-lithium-polymer-battery-mobile-phones](https://www.lithiumlifepo4battery.com/quality-13776872-3-7v-2750mah-rechargeable-lithium-polymer-battery-mobile-phones)

### 2.3 Large (se diseña)

* **~4000 mAh manteniendo huella** mediante **pack 1S2P** (apilado)

  * Ejemplos de fichas donde aparece como **103450 1S2P 4000 mAh**:

    * [https://www.everychina.com/p-z52fad55-119498303-rechargeable-li-polymer-battery-pack-103450-1s2p-3-7v-4000mah.html](https://www.everychina.com/p-z52fad55-119498303-rechargeable-li-polymer-battery-pack-103450-1s2p-3-7v-4000mah.html)
    * [https://www.lithiumbatteriescell.com/sale-50506194-rechargeable-li-polymer-battery-pack-103450-1s2p-3-7v-4000mah.html](https://www.lithiumbatteriescell.com/sale-50506194-rechargeable-li-polymer-battery-pack-103450-1s2p-3-7v-4000mah.html)
  * Medida práctica a asumir (pack): **≈ 20 × 34 × 54 mm** con tolerancias y variación por PCM/cables.

---

## 3) Sistema de iluminación ARES (v4) — Medium/Large (SIN booster 5V, visible ≈50 m)

### 3.1 Arquitectura visual (confirmada)

* **2 zonas LED** (solo en Medium/Large), una a cada lado largo.
* Cada zona es una **“L”** (no una tira recta):

  * **Tramo largo:** recorre ~**3/4** del lado largo.
  * **Tramo corto:** recorre ~**1/2** del lado corto.
* Son **dos Ls opuestas** (en esquinas contrarias) y **no se tocan**.
* **Las 2 Ls son multicolor** (el usuario puede elegir color) mediante **mezcla RGB por PWM**.

### 3.2 Hardware de luz (decisión final)

* **Tipo:** LEDs SMD **1206** de **alta intensidad** y gran ángulo (≈120°–150°).
* **Cantidad:** **12 LEDs total** → **6 por cada L**.
* **Distribución por cada L:** **2 rojos + 2 verdes + 2 azules**.
* Objetivo óptico: luz uniforme tipo “neón” usando **difusor/light‑pipe** + cámara reflectante.

**Referencias sugeridas (para fabricante)**

* **Rojo 1206:** Kingbright **AP3216SURCK** (Vf 1.9–2.1 V).
* **Verde 1206:** Kingbright **AP3216ZGC** (Vf 3.2–3.3 V).
* **Azul 1206:** Kingbright **AP3216PBC/Z** (Vf 3.0–3.2 V).

### 3.3 Layout en la L (uniformidad real)

* Recorrido objetivo (a ajustar cuando CAD esté cerrado):

  * Lado largo: **≈44 mm**
  * Lado corto: **≈18 mm**
  * Total: **≈62 mm**
* Con **6 LEDs**: separación media ≈ **10 mm**.
* Orden recomendado para mezcla homogénea a lo largo de la guía:

  * **B – R – G – B – R – G** (desde el extremo del lado corto, pasando la esquina y siguiendo el lado largo).

### 3.4 Óptica/carcasa (clave del efecto “tira”)

* **Salida por chaflán 45°** para visibilidad lateral.
* **Difusor:** policarbonato **frosted/mate**.
* **Interior reflectante:** blanco mate o metalizado para homogeneizar.
* **Anti light‑bleeding:** tabiques internos / material negro donde haga falta para que la luz salga solo por la “L”.

---

## 4) LEDs — conexión eléctrica (SIN booster 5V)

### 4.1 Alimentación

* **VBAT directa (LiPo 1S): 3.0–4.2 V**.

### 4.2 Topología eléctrica (simple y robusta)

* **Ánodo** de cada LED → **VBAT** a través de su **resistencia**.
* **Cátodo** → conmutación a GND por **MOSFET N (low‑side)**.

### 4.3 Control (para no cargar GPIO)

* Solo **3 canales PWM** para toda la unidad: **R / G / B**.
* **3 MOSFET N** (SOT‑23) como interruptores a GND.

  * Ejemplos típicos: **AO3400A / Si2302** (equivalentes válidos).

### 4.4 Resistencias (guía de partida; se ajusta en test)

Objetivo inicial: **≈10 mA por LED** a VBAT = 4.2 V.

* **Rojo (Vf≈2.0 V):** R ≈ (4.2–2.0)/0.01 ≈ **220 Ω**
* **Verde/Azul (Vf≈3.2 V):** R ≈ (4.2–3.2)/0.01 ≈ **100 Ω**
* Recomendación: **0805 mínimo** (mejor disipación y fiabilidad térmica).

> Si se quiere “más faro”, se hace con **PWM + duty** (pico) y límites térmicos, no subiendo corriente fija sin control.

### 4.5 Alternativas (solo para trazabilidad; descartadas en V4)

* **WS2812/SK6812 direccionables**: requieren rail estable (habitual 5 V) y tienden a añadir complejidad/EMI.

---

## 5) Firmware de luz (color + ahorro + encontrar)

### 5.1 Modos

* **Modo “Encontrar” (prioridad):**

  * **Parpadeo 1 Hz** (0.5 s ON / 0.5 s OFF).
  * **Timeout máximo 15 min**.
  * Color recomendado por visibilidad: **Cian (G+B)** o **Blanco (R+G+B)**.
* **Modo notificación/estado (“latido”):** brillo bajo‑medio (p. ej. 10–20%), pulsación suave.
* **Batería baja:** patrón rojo + reducción de brillo global.

### 5.2 Compensación por voltaje (importante)

* Cuando VBAT baja (≈3.3–3.4 V), **G/B** pierden fuerza antes que R (Vf más alto).
* Solución: **tabla de calibración** (LUT) que ajuste duty R/G/B para mantener color consistente.

### 5.3 Extra opcional

* Apagar LEDs durante ráfagas TX del módem (si fuese necesario) para limpieza RF máxima.

---

## 6) Energía — “cómo fluye” (arquitectura clara por módulos)

### 6.1 Voltajes base

* LiPo 1S:

  * **4.2 V** cargada
  * **3.7 V** nominal
  * **≈3.0 V** descargada (según cutoff)

### 6.2 Módulo B (batería)

* **Entrada de carga desde dock magnético:** **5 V**.
* Dentro del módulo B:

  * **Cargador LiPo 1S** (CC/CV a 4.2 V).
  * **Protección 1S** (sobre/infra‑voltaje, sobrecorriente, corto).
  * **NTC 10k** pegado a celda (corte/limitación por temperatura).
* **Salida hacia módulo A:** **VBAT cruda (3.0–4.2 V) + GND** por contacto interno.
* **No se usa LED verde dedicado en la batería** (la batería estará casi siempre acoplada y se carga por dock; el estado se indica por firmware/telemetría).

### 6.3 Módulo A (chip) *(Diseño y componentes abiertos a cambios para optimizar rendimiento/consumo)*

* Recibe **VBAT** y regula:

  * **3.3 V** (MCU/sensores/GNSS si aplica)
  * **1.8 V** si algún chip lo necesita
* Si el módem celular requiere rail estable:

  * o se alimenta desde VBAT si lo tolera,
  * o se añade **buck‑boost** a rail fijo (p. ej. 3.8 V) para evitar caídas con picos.

### 6.4 Picos de corriente (LTE/GNSS) — evitar cuello de botella en contactos

* No usar “1 pin + 1 pin” para potencia.
* Recomendación mínima:

  * **2–3 pines VBAT en paralelo**
  * **2–3 pines GND en paralelo**
* Recomendación “muy robusta” (si cabe): **8 pines total = 4×VBAT + 4×GND**.
* Además: cámara seca / laberinto de sellado alrededor de la zona de pines.

---

## 7) Carga magnética: criterios, opciones y decisión

### 7.1 Criterios obligatorios (calidad + outdoor)

* Prioridad: **calidad**, **fuerza magnética**, estabilidad mecánica y resistencia a corrosión.
* Debe ser **resistente a agua/polvo**: idealmente un sistema que declare **IP mated** (p. ej. IP67/64 según modelo) y además montado en **cavidad recesada** con drenaje.
* **Chapado oro** y materiales aptos para exterior.
* Corriente objetivo: **≥2 A a 5 V**.

### 7.2 Opción “producción” (referencia de calidad)

* **TE Connectivity — Magnetic pogo pin cable assemblies (wearables)**

  * [https://www.te.com/es/products/cable-assemblies/copper-cable-assemblies/multimedia-cable-assemblies/magnetic-pogo-pin-cable-assemblies.html](https://www.te.com/es/products/cable-assemblies/copper-cable-assemblies/multimedia-cable-assemblies/magnetic-pogo-pin-cable-assemblies.html)

### 7.3 Alternativa premium

* **Rosenberger RoPD**

  * [https://www.rosenberger.com/product/ropd/](https://www.rosenberger.com/product/ropd/)

### 7.4 Prototipo rápido (validación mecánica)

* **HYTEPRO** (muestras rápidas, 2–3 A, fuerza magnética especificada en fichas)

  * M826 (2A): [https://www.hyte.pro/product/m826.html](https://www.hyte.pro/product/m826.html)
  * M417P (3A): [https://www.hyte.pro/product/m417p.html](https://www.hyte.pro/product/m417p.html)

### 7.5 Estado de decisión

* **Aún no se congela el modelo exacto.**
* Siguiente paso: seleccionar 2–3 candidatos (TE / Rosenberger / HYTEPRO) y compararlos por:

  * IP mated declarado, fuerza magnética, ciclos de acoplamiento, corrosión, disponibilidad y coste.

---

### 7.6 Decisión operativa provisional

* Prototipos: HYTEPRO (validación rápida).
* Producción: TE (calidad + consistencia), salvo que Rosenberger sea viable en tamaño/coste.
* Prototipos: HYTEPRO (validación rápida).
* Producción: TE (calidad + consistencia).

---

## 8) Checklist para actualizar documentación anterior

1. Sustituir batería Medium por **123450 ~2750 mAh** y Large por **pack 1S2P ~4000 mAh**.
2. Congelar hueco interno Medium/Large a **36×58 mm** (paredes interiores).
3. Documentar que **Medium y Large comparten el mismo cartucho**, cambia solo grosor.
4. Eliminar “LED verde en módulo batería”: carga magnética = batería casi siempre conectada.
5. LEDS Medium/Large:

   * 2 zonas en “L” opuestas
   * **6 LEDs por L** (12 total) con **2R+2G+2B por L**
   * chaflán 45° + light‑pipe/difusor
   * colores por mezcla PWM + modo parpadeo para “Encontrar”
6. Eléctrica:

   * **SIN booster 5V** en V4 (LEDs 1206 a VBAT + resistencias + MOSFET low‑side)
   * límites firmware: 35% default, 50% max, 15 min cap.
7. Carga magnética:

   * prototipo HYTEPRO
   * producción TE Connectivity
