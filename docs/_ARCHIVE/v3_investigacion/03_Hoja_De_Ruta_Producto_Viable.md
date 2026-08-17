> **NOTA DE ACTUALIZACIÓN (Enero 2026):** Este documento forma parte del archivo de investigación. Las decisiones y componentes aquí analizados (ej. `Quectel BG96`, `MPU6050`) han sido superados. Para la especificación final y definitiva del hardware, por favor consulte **`docs/investigacion_tracker_diy/PRODUTO/Hardwear.txt` (v3.6)**, que establece la arquitectura modular basada en `LilyGo T-SIM7000G S3` y `BMI270`.

---

# 03 - Hoja de Ruta para un Producto Viable: De Prototipo DIY a Solución Profesional

Este documento presenta una "hoja de ruta maestra" para transformar la idea de un prototipo DIY en un **producto comercial viable, duradero (10-15 años) y competitivo**, basándose en las tecnologías más actuales y profesionales. Se aborda la ingeniería de producto necesaria para superar las limitaciones de un enfoque puramente "maker".

---

### 1. La Lógica del Firmware: El "Secreto" de la Batería Infinita

Para que el tracker no muera en 4 horas enviando datos a 45 km/h, es esencial implementar una máquina de estados gestionada por interrupciones, utilizando un **Acelerómetro (IMU)** de bajo consumo como el **LIS3DH** o **BMA400**. Esto es la clave para abordar el dilema de la **"Autonomía mínima realista"** planteado en `00_Cuestiones_Criticas_De_Diseño.md`.

**El Algoritmo "Smart Dog":**

1.  **Estado "Coma" (Deep Sleep):**
    *   El microcontrolador (ESP32/Nordic), el Módem LTE y el GPS están **físicamente apagados** (corriente cortada por MOSFET).
    *   Solo el acelerómetro está despierto (consumo ridículo: <5 microamperios).
    *   *Situación:* El perro está durmiendo en el sofá, y el dispositivo consume la mínima energía posible, prolongando la autonomía a meses.

2.  **Evento "Shake" (Interrupción):**
    *   El perro se levanta o empieza a moverse. El acelerómetro detecta vibración y envía una señal eléctrica a un pin del microcontrolador.
    *   El microcontrolador se despierta (boot en milisegundos), activando el sistema.

3.  **Estado "Validación de Movimiento":**
    *   El microcontrolador analiza el patrón de movimiento durante unos segundos.
    *   ¿Es solo un rascado? -> Vuelve a dormir.
    *   ¿Es un paseo/carrera constante? -> **Activa el GPS** y el módem.

4.  **Estado "Tracking Dinámico" (La clave de la velocidad y eficiencia):**
    *   Aquí se ajusta la tasa de refresco del GPS y la transmisión de datos según la velocidad y actividad detectadas:
        *   **Velocidad < 3 km/h:** GPS cada 5 minutos (o WiFi sniffing si hay redes cercanas para ahorrar batería y datos).
        *   **Velocidad > 15 km/h (Corriendo):** GPS cada 10 o 30 segundos (Modo ráfaga para seguimiento en tiempo casi real a alta velocidad).
    *   *Transmisión:* Para ahorrar datos y batería, no se envía cada punto inmediatamente. Se acumulan 5 o 10 puntos en un paquete pequeño y se envían de golpe por LTE-M (Buffer), a menos que se active el "Modo Emergencia/Perdido" desde la app, donde se forzará el envío en tiempo real (vinculado al dilema de **"¿Necesitas comandos downlink de verdad?"**).

---

### 2. Alternativas Hardware: ¿Qué usan los profesionales en 2026?

La placa **Walter** es fantástica para prototipar, pero si se busca durabilidad de 15 años y optimización extrema para un producto final, hay opciones que dominan la industria hoy día y son "el estándar de oro". Se debe considerar un **System-in-Package (SiP)** que integra todo en un solo chip.

#### La Opción "Industrial": Nordic Semiconductor nRF9160 / nRF9161

En lugar de tener dos chips separados (microcontrolador ESP32 + módem Sequans) como hace Walter, Nordic ha creado un chip que lo tiene **TODO en uno (SiP - System in Package)**.

*   **Por qué es mejor que Walter para un producto final:**
    *   **Tamaño:** Es minúsculo (10x16mm), lo que permite diseños compactos para collares de perros pequeños.
    *   **Consumo:** Está diseñado desde cero para IoT de bajo consumo. Su gestión de energía (ej. 2.7µA en modo PSM) es superior a la combinación ESP32+Sequans, impactando directamente en la **"Autonomía mínima realista"**.
    *   **Durabilidad (10-15 años):** Nordic es un gigante de la industria, y sus chips tienen soporte a larguísimo plazo.
    *   **GPS Asistido (A-GPS):** Nordic tiene un servicio en la nube que envía al chip la posición de los satélites por internet. Esto hace que el GPS fije la posición en **3 segundos** (en lugar de 40s), ahorrando muchísima batería en cada "fix".

*   **Desventaja:** Es más difícil de programar que un ESP32 (usa Zephyr RTOS en lugar de Arduino/PlatformIO), lo que implica una curva de aprendizaje más alta o la necesidad de un ingeniero especializado.

#### La Opción "Sin quebraderos de cabeza": Blues Wireless Notecard

Si la prioridad absoluta es "Pago único, sin mensualidad y que funcione siempre", esta es una opción a considerar, abordando directamente el dilema de **"¿SIM del usuario o SIM tuya (suscripción)?"**.

*   **Qué es:** Un módulo que ya incluye el módem, la SIM y **500MB de datos prepagados por 10 años** en el precio del hardware.
*   **Ventaja:** Elimina la complejidad de negociar con operadores, configurar APNs o preocuparse por la caducidad de la SIM. Proporciona una solución "plug-and-play" para la conectividad.
*   **Desventaja:** Es más caro de entrada (unos 50-60€ por módulo) y ofrece menos control sobre el firmware del módem.

---

### 3. Innovaciones y "Future-Proofing" (Para que dure 15 años)

Si el objetivo es lanzar un producto que se mantenga competitivo y funcional durante más de una década, se deben incorporar las siguientes innovaciones:

1.  **Antenas "Virtual Antenna" (Ignion):**
    *   Olvídate de cables y pegatinas flexibles que se rompen o se desconectan con el movimiento. Las antenas de Ignion son chips cerámicos SMD (se sueldan a la placa).
    *   **Ventajas:** Usan la propia placa electrónica (PCB) para amplificar la señal. Son robustas, no se rompen con golpes y son omnidireccionales (perfectas para un perro que se revuelca).

2.  **Baterías de Estado Sólido o Li-Ion con Ánodo de Silicio:**
    *   *Problema:* Las baterías LiPo normales se degradan en 3-4 años.
    *   *Solución:* Busca celdas de **ánodo de silicio** (mayor densidad, más pequeñas) o baterías diseñadas para rangos de temperatura extendidos (aguantan el frío del bosque y el calor del verano). Esto impacta directamente en la durabilidad del producto y el mantenimiento de la **"Autonomía mínima realista"** a lo largo del tiempo.

3.  **Carga Inalámbrica (Qi):**
    *   **Esencial:** Eliminar el puerto USB es la única forma de garantizar que el dispositivo sea sumergible (IP68) durante 10 años. Los puertos USB y sus tapas de goma son puntos de fallo comunes para la estanqueidad. La carga inalámbrica resuelve este problema.

4.  **LTE-M y el Apagado de Redes:**
    *   2G y 3G están desapareciendo.
    *   4G y 5G se quedarán. **LTE-M y NB-IoT** son parte del estándar 5G, lo que garantiza la disponibilidad de la red para los próximos 15 años. No se debe depender de nada que use "2G Fallback" como conexión principal.

---

### 4. ¿Qué pasa si el perro se pierde donde NO hay cobertura? (El problema del Bosque profundo)

Este es el núcleo del dilema **"¿Debe funcionar cuando NO hay cobertura móvil?"**. Si te vas a los Pirineos o zonas remotas, ni 1NCE ni Movistar te salvarán.

*   **Innovación Híbrida (Lo que hacen los Garmin de caza):**
    *   Tu dispositivo debe tener **Radiofrecuencia Directa** (como LoRa, pero punto a punto, no necesita infraestructura de red).
    *   *Funcionamiento:* Si el perro está a menos de 5-10km de ti en el bosque y no hay cobertura móvil, el collar envía la señal directamente a tu móvil (necesitarías un pequeño receptor o que tu móvil soporte protocolos nuevos, aunque lo normal es un receptor pequeño tipo llavero).
    *   *Alternativa más barata:* **Bluetooth Long Range (Coded PHY)**. El chip **nRF52840** (que viene dentro del nRF9160 de Nordic) soporta Bluetooth 5 largo alcance. Puede llegar a 1km en línea de visión en entornos abiertos.

### 5. Resumen: ¿Qué necesitas realmente para tu PRODUCTO VIABLE?

Para pasar de un prototipo DIY a un producto final comercializable:

1.  **Diseño de PCB Propia (Custom):**
    *   Integrar solo los componentes necesarios (basado en el nRF9160).
    *   Incluir antenas Ignion y cargador inalámbrico directamente en el diseño.
    *   *Resultado:* Una placa del tamaño de una moneda de 2 euros. Coste de fabricación: ~30-40€/unidad en volumen.

2.  **La Carcasa (Mecánica):**
    *   Debe ser de **Policarbonato** (PC) o ASA (resiste rayos UV) para durabilidad.
    *   **Estanqueidad:** Soldadura por ultrasonidos o tornillos con Loctite y junta tórica para garantizar IP68.
    *   **Seguridad:** A prueba de mordiscos.

3.  **El Plan de Negocio "Pago Único":**
    *   Usando **1NCE** (10€/10 años) o **Blues Wireless Notecard**.
    *   *Coste Base Estimado:* Hardware (~40€) + SIM (10€) + Batería/Caja (~10€) = **~60€**.
    *   *Precio de Venta Sugerido:* 120-150€ (un solo pago). Este modelo es muy atractivo frente a competidores que cobran suscripciones mensuales.

### Links y Referencias Proactivas

*   **El Rey del Hardware:** [Nordic Semiconductor nRF9160](https://www.nordicsemi.com/Products/nRF9160)
*   **La Conectividad Fácil:** [Blues Wireless](https://blues.io/)
*   **Antenas Indestructibles:** [Ignion Virtual Antenna](https://ignion.io/)
*   **Fabricación de PCB:** [PCBWay](https://www.pcbway.com/) o [JLCPCB](https://jlcpcb.com/)
*   **Carga Inalámbrica:** Chips como el **LTC4124**

**Conclusión:** El vídeo es un excelente punto de partida "Maker", pero para lo que tú pides (15 años, 45km/h, bosque/ciudad, producto serio), la ruta es **Nordic nRF9160 + Antenas Cerámicas Ignion + Carga Inalámbrica + 1NCE**.
