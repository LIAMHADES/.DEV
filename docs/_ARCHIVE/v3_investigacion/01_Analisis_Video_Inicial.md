> **NOTA DE ACTUALIZACIÓN (Enero 2026):** Este documento forma parte del archivo de investigación. Las decisiones y componentes aquí analizados (ej. `Quectel BG96`, `MPU6050`) han sido superados. Para la especificación final y definitiva del hardware, por favor consulte **`docs/investigacion_tracker_diy/PRODUTO/Hardwear.txt` (v3.6)**, que establece la arquitectura modular basada en `LilyGo T-SIM7000G S3` y `BMI270`.

---

# 01 - Análisis Detallado del Vídeo: Prototipo DIY de Tracker GPS para Perros

Este documento extrae toda la información técnica, los componentes, las pruebas y los fallos del vídeo, orientándolo específicamente a tu proyecto de **construir un tracker para perros de alta precisión y velocidad**. Aquí tienes el desglose completo para que puedas hacerlo a tu manera ("DIY").

---

### 1. El Hardware: ¿Qué utiliza exactamente?

El "cerebro" del proyecto no es un Arduino común ni una Raspberry Pi. Es una placa muy específica diseñada en Bélgica.

*   **Nombre de la Placa:** **Walter** (creada por DPTechnics).
*   **Componentes Clave (System-on-Module):**
    *   **Microcontrolador:** **ESP32-S3**. Esto es genial porque es potente, tiene WiFi y Bluetooth nativos, y es compatible con el entorno de Arduino/PlatformIO (fácil de programar). Su elección subraya la flexibilidad y potencia necesarias para un sistema de gestión de energía complejo y diversas opciones de conectividad de respaldo.
    *   **Módem:** **Sequans Monarch 2 (GM02SP)**. Este chip maneja la conexión celular (LTE-M y NB-IoT) y el GPS (GNSS) todo en uno. Es crucial para el objetivo de "precisión y velocidad".
*   **Consumo energético:** Extremadamente bajo. En modo "dormido" consume solo **9.5 microamperios**. Esta cifra es clave para el dilema de **"Autonomía mínima realista"** planteado en `00_Cuestiones_Criticas_De_Diseño.md`, ya que permite que el dispositivo dure años con una batería pequeña si se configura bien la lógica de sueño profundo.
*   **Antenas:** Utiliza antenas externas conectadas por cables u.FL.
    *   *Importante:* Para el GPS usa una **antena pasiva** (marca **Taoglas**). El creador explica que evita las antenas activas porque consumen energía de forma impredecible. Este es un detalle crítico para la gestión de la autonomía.

### 2. La Tecnología de Comunicación (Clave para tu perro)

Para que el tracker funcione a **45 km/h** y tenga cobertura real (objetivo de tu proyecto), el vídeo descarta tecnologías como LoRaWAN (demasiado lento) o Sigfox.

*   **Tecnología recomendada:** **LTE-M** (Long Term Evolution for Machines).
    *   **¿Por qué?** Tiene una latencia muy baja (<200ms). Esto significa que puedes ver dónde está el perro casi en tiempo real, cumpliendo el requisito de "velocidad" para un perro en movimiento.
    *   **Diferencia con NB-IoT:** El vídeo menciona que NB-IoT tiene mejor penetración en edificios, pero puede tener un retraso de segundos o minutos. Para un perro corriendo a 45 km/h, se prioriza LTE-M por su menor latencia.
*   **Backup (Tu requisito de seguridad):** El sistema tiene **WiFi y Bluetooth** integrados (gracias al ESP32).
    *   *Uso:* Si el perro está cerca (ej. dentro de casa o en el parque a 50 metros), puedes usar Bluetooth/WiFi para ahorrar batería y datos. Cuando se aleja, salta a LTE-M. Esto aborda parcialmente el dilema de **"¿Debe funcionar cuando NO hay cobertura móvil?"** al ofrecer alternativas para escenarios de proximidad.

### 3. Tarjetas SIM y Costos (Recomendaciones del vídeo)

Para que el dispositivo tenga "internet" propio y envíe la posición a tu móvil, necesitas una SIM especial para IoT (Internet de las Cosas). El vídeo analiza tres:

1.  **1NCE (La más recomendada para ti):**
    *   **Precio:** Un pago único de **~10 USD/EUR**.
    *   **Ventaja:** Te da servicio por **10 años** con 500MB de datos.
    *   **Por qué es ideal:** Es un modelo "paga una vez y olvídate", sin cuotas mensuales, abordando directamente el dilema de **"¿SIM del usuario o SIM tuya (suscripción)?"** al favorecer una SIM incluida con un coste inicial.
2.  **Hologram:**
    *   **Ventaja:** Excelente panel de control y cobertura global (roaming agresivo).
    *   **Desventaja:** Suele tener costos mensuales o por uso más elevados que 1NCE.
3.  **Soracom:** Viene incluida en la caja de la placa Walter, útil para empezar rápido.

### 4. Resultados de las Pruebas y FALLOS (Muy importante)

El vídeo somete al dispositivo a tres pruebas. Aquí es donde aprendemos qué esperar:

*   **Prueba de velocidad (Coche):**
    *   *Resultado:* Éxito. Logró conectarse a la red LTE y obtener un "fix" de GPS en **4 segundos**.
    *   *Dato:* El GPS funcionó incluso con el cristal del coche de por medio. La precisión fue muy alta en movimiento, confirmando la viabilidad para el seguimiento de "perro a 45 km/h".
*   **Prueba "Brutal" (Escalera de hormigón cerrada):**
    *   *Resultado:* Conectó a la red celular (pudo enviar datos), **PERO el GPS falló**.
    *   *Lección:* El GPS necesita "vista al cielo". Si el perro entra en un túnel, sótano o edificio muy denso, no tendrás ubicación GPS exacta. **Esto responde directamente a una faceta del dilema "¿Debe funcionar cuando NO hay cobertura móvil?"**, específicamente en entornos urbanos o subterráneos donde la señal satelital se bloquea.
    *   *Tu solución de Backup:* El vídeo muestra que, aunque falle el GPS, la red celular te da una **ubicación aproximada basada en triangulación de torres de telefonía** (Cell ID). No es exacta (margen de cientos de metros), pero te dirá en qué zona está el perro, ofreciendo un respaldo vital.

### 5. Software y Cómo montarlo (Open Source)

El creador del vídeo menciona que todo es "Open Source" (Hardware y Software), lo que facilita el desarrollo "DIY".

*   **Firmware:** El código para hacer funcionar el módem Sequans con el ESP32 está disponible.
*   **Librerías:** Utilizan librerías propias de **Walter** para gestionar la conexión y el GPS fácilmente.
*   **Visualización (App):** En el vídeo usan una demo llamada "QuickSpot" y también "Flasher.meshtastic.org".
    *   *Tu caso:* Como quieres hacerlo a tu manera, al ser un ESP32, podrías programarlo para que envíe los datos a **Blynk**, **Home Assistant**, o un bot de **Telegram** en tu móvil, integrándose con tu backend FastAPI.

### 6. Resumen para tu Proyecto "Tracker para Perro DIY"

Si quieres replicar esto para tu perro con las especificaciones que pides, esto es lo que necesitas comprar y hacer:

**Lista de la compra estimada:**
1.  **Placa:** "Walter" (aprox. 60€ - 70€). *Nota: No está en AliExpress, se compra en Crowd Supply o distribuidores europeos.*
2.  **Batería:** Una LiPo pequeña (ej. 1000mAh) con conector JST.
3.  **SIM:** Tarjeta **1NCE** (10€ pago único).
4.  **Caja:** Impresión 3D (diseño robusto para el collar).
5.  **Antenas:** 1 Antena flexible LTE y 1 Antena cerámica o flexible GPS (Taoglas).

**Presupuesto total estimado:** Unos **90€ - 110€** (pago único, sin mensualidades).

**Características que obtendrás:**
*   **Precisión:** GPS Real (GNSS) con error de pocos metros, fundamental para geovallas.
*   **Velocidad:** Soporta 45 km/h sin problemas gracias a LTE-M, clave para perros activos.
*   **Backup:** Si falla el GPS, usas triangulación celular. Si falla el celular, usas WiFi/Bluetooth si está cerca.
*   **Actualizaciones:** Al ser ESP32, puedes actualizar el código por aire (OTA), permitiendo evolucionar el producto.

**El producto "Houdini M1":**
Al final del vídeo, menciona su producto "Houdini M1". *Ojo con esto:* El Houdini M1 original usa tecnología **LoRa (Meshtastic)**, no celular. **Para lo que tú quieres (velocidad y cobertura total sin depender de otros nodos), la placa Walter con LTE-M es superior** a la versión LoRa del Houdini para rastrear un perro que se mueve rápido y lejos. Esto refuerza la elección de LTE-M sobre LoRa para el propósito principal de tu tracker.

**Recomendación final:** Usa la placa **Walter** con una SIM de **1NCE**. Programa el ESP32 para que envíe la ubicación cada 30 segundos si detecta movimiento (acelerómetro o cambio de GPS) y cada 1 hora si está quieto para ahorrar batería. La implementación del acelerómetro es vital para una gestión eficiente de la **"Autonomía mínima realista"**.
