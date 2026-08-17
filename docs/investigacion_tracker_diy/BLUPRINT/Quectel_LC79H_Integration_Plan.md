## Documento — Requisitos e integración del **Quectel LC79H (LC79HALMD)** en ARES (GNSS v1)

### 1) Qué es y qué NO es

* **LC79H es el receptor GNSS** (el “cerebro” que calcula la posición).
* **NO es la antena**. Necesita **antena GNSS externa** (interna en tu carcasa, pero físicamente separada del módulo) y su circuito RF de entrada.
* Su ventaja clave para tu objetivo: **dual-band L1+L5** + multi-constelación → mejor robustez en **ciudad/bosque** (menos multipath) y más fácil cumplir **p95 ≤10 m**.

---

### 2) Lo que debe entregar (contrato de datos)

El sistema (módulo + firmware) debe poder obtener y reportar:

* **Latitud / Longitud**
* **Altitud**
* **Velocidad (ground speed)**
* **Rumbo / course over ground**
* **Timestamp GNSS/UTC**
* **Calidad del fix** (para filtrar puntos malos y cumplir p95):

  * Tipo de fix (no/2D/3D)
  * Satélites usados
  * **DOP (HDOP/PDOP)** y/o **hAcc/vAcc** si el módulo lo expone
  * Ideal: **C/N0 / SNR** o indicador de señal

Esto es obligatorio para:

* No confundir “ida/vuelta” con “no se movió”
* Filtrar outliers en bosque/ciudad
* Predecir 2–4 s de trayectoria con (velocidad+rumbo) si hay pérdida temporal de uplink

---

### 3) Modos y frecuencia GNSS (cómo lo vas a usar)

* **LIVE / búsqueda intensa:** 1–2 s
* **Normal actividad:** 10–15 s
* **Seguro / reposo:** 30–60 s si la IMU confirma poco movimiento
  El GNSS no se usa para “pasos”; eso lo hace IMU. El GNSS se usa para **ubicación y validación**.

---

### 4) A-GNSS (obligatorio)

* Debe soportar **A-GNSS** (inyección/uso de datos de asistencia) para:

  * **Warm start objetivo 5–10 s**
  * **Cold start objetivo ≤30 s**
* Backend/app debe poder entregar esos datos cuando toque.

---

### 5) Requisitos eléctricos (críticos para que funcione estable)

**5.1 Alimentación principal**

* El LC79H trabaja típicamente con **VCC ~1.8 V** (confirmar rango exacto en datasheet).
* En ARES, eso implica:

  * Un **rail 1.8 V dedicado** (idealmente regulador/LDO “limpio” para GNSS).
  * Decoupling muy cercano (condensadores pegados al pin VCC).

**5.2 Backup (warm start real)**

* Debe tener **V_BCKP** alimentado (típicamente 1.8 V) para mantener estado/RTC y mejorar TTFF warm.
* En PCB: desacople cercano a V_BCKP (y protección si aplica).
* Ideal: poder **cortar/controlar V_BCKP** desde MCU para “reset duro” si el módulo entra en estado raro.

**5.3 Niveles lógicos (importante con ESP32-S3)**

* ESP32 es **3.3 V**. Si el LC79H usa **IO 1.8 V**, necesitas **level shifting** en UART y líneas de control (reset, enable, etc.) para no:

  * dañar IO
  * tener comunicación inestable
* Regla: **no conectar UART directo** si los niveles no coinciden.

**5.4 Reset/control**

* Debe existir una forma de **reset controlable** (pin RESET/ENABLE o equivalente) para recuperación automática.
* Firmware debe incluir watchdog lógico: si GNSS se queda sin fix/colgado → reset controlado.

---

### 6) Requisitos RF (la parte que determina precisión real)

**6.1 Entrada RF**

* El módulo tiene un pin RF (entrada GNSS) que debe conectarse a la antena mediante:

  * **línea RF corta**
  * **impedancia controlada 50 Ω** (cuando definamos antena y stackup)
* Muy recomendable reservar footprint de:

  * **red de adaptación (π matching)** cerca del pin RF
  * **protección ESD específica RF** (muy baja capacitancia)
  * **filtro SAW / pre-filtro** si la coexistencia con LTE lo exige (tu caso es probable)

**6.2 Coexistencia LTE**

* La transmisión LTE puede degradar GNSS por acoplo/interferencia.
* La mitigación “de diseño” (sin magia):

  * separación física GNSS vs LTE
  * filtrado RF (SAW si hace falta)
  * plano de masa sólido
  * evitar rutas ruidosas cerca de RF

> Punto clave: “zona prohibida debajo/encima” normalmente la impone la **antena**, no el módulo LC79H. El módulo puede ir en PCB sin comerse una zona enorme; lo que manda es el tipo de antena que elijas después.

---

### 7) Requisitos mecánicos e integración en tu PCB (40×70, altura ≤15)

* El LC79H (módulo) es **pequeño y bajo**: no necesita “sombrero” ni placa aparte.
* Va soldado normal en la PCB (SMD).
* Reglas prácticas de colocación:

  * Colocarlo **cerca del borde** donde estará la antena GNSS (para RF corto).
  * Mantenerlo lejos de fuentes ruidosas: **DC/DC**, líneas rápidas, cristal/clock, y lo más posible del módem LTE.
  * Debajo del módulo: plano de GND y retornos limpios (4 capas recomendado para estabilidad y RF).

---

### 8) Checklist de “funciona o no funciona” (lo mínimo que debe cumplirse en PCB)

Para considerar LC79H “bien integrado” antes de pasar a antena:

1. **Rail 1.8 V definido** y desacoplado cerca del módulo.
2. **V_BCKP definido** (con desacople) para warm start real.
3. **UART con niveles correctos** (level shifting si hace falta).
4. **RF_IN con**

   * pista corta
   * 50 Ω planificado
   * footprint de matching + ESD RF
   * opción de filtro (SAW) si luego en tests hace falta
5. **Reset/control** desde MCU para recuperación.
6. **Separación física** razonable GNSS vs LTE vs DC/DC (layout por zonas).

---

### 9) Qué implica para la fase siguiente (antena)

Como LC79H es **L1+L5**, la antena que definamos debe:

* Soportar **L1 y L5**
* Ser **interna**, robusta, y compatible con tu PCB/carcasa
* Definir keep-out real (metales, tornillos, leds, batería, etc.)
* Permitir rendimiento en ciudad/bosque para cumplir p95 ≤10 m

---