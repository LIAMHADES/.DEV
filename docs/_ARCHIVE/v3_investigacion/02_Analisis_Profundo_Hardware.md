> **NOTA DE ACTUALIZACIÓN (Enero 2026):** Este documento forma parte del archivo de investigación. Las decisiones y componentes aquí analizados (ej. `Quectel BG96`, `MPU6050`) han sido superados. Para la especificación final y definitiva del hardware, por favor consulte **`docs/investigacion_tracker_diy/PRODUTO/Hardwear.txt` (v3.6)**, que establece la arquitectura modular basada en `LilyGo T-SIM7000G S3` y `BMI270`.

---

# 02 - Análisis Profundo de Hardware, Energía y Construcción del Tracker DIY

Este documento profundiza en comparativas de hardware, gestión de energía y detalles de construcción mencionados en el vídeo, cruciales para las decisiones de diseño del proyecto ARES GPS.

---

### 1. La Gran Comparativa: Walter vs. RAK5010

El vídeo compara la placa **Walter** con su competencia directa, la **RAK5010**. Esta comparativa es fundamental para entender los *trade-offs* entre facilidad de desarrollo, eficiencia energética y funcionalidad, aspectos clave para el dilema de **"Autonomía mínima realista"** planteado en `00_Cuestiones_Criticas_De_Diseño.md`.

*   **RAK5010 (La alternativa):**
    *   *Ventaja:* Viene con conector de batería JST y puerto para **panel solar** integrado, una característica interesante para extender la autonomía.
    *   *Desventaja (Y por qué el vídeo prefiere Walter):* Usa un software más cerrado ("RUI3 toolchain") y combina un chip Nordic para el Bluetooth, lo que hace la programación mucho más compleja. Además, consume más energía en comparación con Walter.
*   **Walter (La ganadora según el vídeo):**
    *   *Ventaja:* Es "Open Source" real, utiliza el entorno estándar de ESP32 (Arduino/PlatformIO), lo que facilita enormemente el desarrollo. Tiene un diseño de hardware más limpio para el bajo consumo.
    *   *Desventaja:* Requiere soldar los cables de la batería o diseñar una pequeña placa base (PCB), ya que no incluye un conector de batería directo tipo "plug-and-play" en la versión básica.

### 2. El Secreto de la Batería: "MOSFET Power Switching"

Este es un detalle de **"oro puro"** para tu proyecto y directamente relacionado con la **"Autonomía mínima realista"**. El vídeo explica *cómo* consiguen que la batería dure años.

*   La placa Walter tiene un **interruptor MOSFET integrado**.
*   **¿Qué significa esto para tu proyecto?** Puedes programar el código para que **corte físicamente la corriente** a los componentes de alto consumo (como el módulo celular y el GPS) cuando el perro está inactivo. No es solo ponerlos en "standby" o "deep sleep", es apagarlos del todo por software.
*   **Dato del vídeo:** En "Deep Sleep" (sueño profundo), la placa Walter consume solo **9.5 microamperios**. Esta cifra, combinada con el MOSFET, es la clave para lograr autonomías de semanas o incluso meses.

### 3. Profundización sobre las Antenas (Detalle Crítico para el Rendimiento)

El vídeo entrevista a uno de los creadores y explica por qué **NO debes usar una antena GPS activa**, un factor que influye directamente en la autonomía y la fiabilidad.

*   **Antenas Activas:** Tienen un amplificador que, aunque mejora la señal, tiene un consumo de energía impredecible (una puede gastar 7mA y otra 60mA). Esto destroza cualquier estimación precisa de la duración de la batería.
*   **La decisión:** Se usan antenas **pasivas**. Aunque captan un poco menos de señal, su consumo es constante y predecible, lo cual es vital para una gestión de energía eficiente.
*   **Recomendación del vídeo:** Se utilizan antenas de la marca **Taoglas**. Son flexibles (tipo pegatina) e ideales para integrar en un collar curvo sin aumentar el volumen.

### 4. Software: Meshstastic vs. Cellular (Aclaración vital para tu Objetivo)

El producto final del creador del vídeo, el **Houdini M1**, usa tecnología **LoRa (Meshtastic)**, no celular.

*   **Aclaración para tu proyecto**: Para rastreo en **tiempo real y alta velocidad** (perro corriendo a 45 km/h), la tecnología celular (**placa Walter con LTE-M**) es superior a LoRa. LoRa tiene mucha latencia y, si no hay otros nodos cerca, se pierde la señal, lo que contradice el objetivo de "precisión y velocidad".

### 5. La Carcasa y el Montaje Físico (Clave para Durabilidad y Seguridad)

El vídeo muestra brevemente el diseño físico y estas consideraciones son cruciales para la robustez y seguridad del dispositivo.

*   **Diseño sin tornillos:** Utiliza un sistema de clips o presión para cerrar la caja.
*   **Material:** Se recomienda impresión 3D resistente o inyección de plástico (Polipropileno, ABS o Policarbonato) si se busca producción en masa.
*   **Sujeción:** La correa del perro pasa **a través** del dispositivo, no colgando de ella. Esto es un detalle de diseño muy importante para:
    *   **Evitar rebotes:** Cuando el perro corre a 45 km/h, el dispositivo no golpea.
    *   **Seguridad:** Reduce la posibilidad de que el perro (o algo más) lo enganche y lo pierda o lo dañe.
    *   **Comodidad:** Más cómodo para el animal.