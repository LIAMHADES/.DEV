> **NOTA DE ACTUALIZACIÓN (Enero 2026):** Este documento forma parte del archivo de investigación. Las decisiones y componentes aquí analizados (ej. `Quectel BG96`, `MPU6050`) han sido superados. Para la especificación final y definitiva del hardware, por favor consulte **`docs/investigacion_tracker_diy/PRODUTO/Hardwear.txt` (v3.6)**, que establece la arquitectura modular basada en `LilyGo T-SIM7000G S3` y `BMI270`.

---

# 00 - Cuestiones Críticas de Diseño del Proyecto ARES GPS

Este documento sirve como punto de partida y registro de las preguntas y dilemas fundamentales que definen la arquitectura y el modelo de negocio del producto. Las decisiones tomadas en respuesta a estas preguntas se reflejan en los documentos de análisis y diseño posteriores.

---

### 1. ¿Debe funcionar cuando NO hay cobertura móvil?

Este es el escenario del "perro de caza" o de rutas por la montaña/bosques profundos.

*   **Dilema:** Si la respuesta es afirmativa, la conectividad celular (LTE-M, NB-IoT) no es suficiente, ya que depende de la infraestructura de las operadoras de telefonía.
*   **Consecuencia:** Se necesita una tecnología de radio de comunicación directa (dispositivo a receptor) o una conexión satelital.
    *   **Opciones:** Radio VHF (estilo Garmin de caza), LoRa (Punto a Punto), o conectividad satelital (más cara).
*   **Impacto:** Esta decisión cambia drásticamente el coste del hardware, el diseño de la antena, el tamaño del dispositivo y la arquitectura de comunicación.

--- 

### 2. ¿SIM del usuario o SIM incluida en el dispositivo?

Este es un dilema de modelo de negocio y experiencia de usuario (UX).

*   **Opción A: SIM del Usuario**
    *   **Ventaja para el negocio:** El coste operativo del servicio de datos recae en el cliente. Reduce la complejidad de la gestión de SIMs.
    *   **Desventaja para el usuario (Fricción):** El usuario debe buscar, comprar y configurar una SIM de IoT compatible, lo cual es una barrera de entrada significativa y una mala experiencia inicial.

*   **Opción B: SIM Incluida (Nuestra)**
    *   **Ventaja para el usuario (Mejor UX):** El dispositivo funciona "al sacarlo de la caja". La experiencia es premium y sin complicaciones.
    *   **Desventaja para el negocio:** Se debe gestionar el ciclo de vida de las SIMs y absorber el coste. Se necesita un modelo para cubrir ese coste (ej. pago único como 1NCE, o una suscripción).

---

### 3. ¿Se necesitan comandos "Downlink" (del servidor al dispositivo)?

*   **Dilema:** ¿Es el dispositivo un simple "emisor de datos" (uplink) o debe ser capaz de recibir y ejecutar órdenes enviadas desde el servidor o la app del usuario (downlink)?
*   **Casos de Uso para Downlink:**
    *   **Activar Modo Perdido:** Forzar al dispositivo a enviar su ubicación cada 5 segundos.
    *   **Cambiar Frecuencia de Reporte:** Ajustar la configuración de envío de datos para ahorrar batería.
    *   **Forzar un "Fix" GPS Ahora:** Pedir una ubicación en este mismo instante.
    *   **Actualizaciones de Firmware (OTA):** Enviar un nuevo software al dispositivo.
*   **Impacto:** La necesidad de un downlink fiable afecta a la elección de la tecnología (LTE-M es mejor que NB-IoT para esto) y a la complejidad del firmware.

---

### 4. ¿Cuál es la autonomía mínima realista aceptable?

Esta pregunta define el equilibrio entre el tamaño de la batería, la frecuencia de actualización y el tamaño físico del dispositivo.

*   **Dilema:** ¿Cuál es el objetivo mínimo que debe cumplir el producto para ser competitivo y útil?
    *   **Opción A (2-3 días):** Aceptable para uso urbano intensivo, pero requiere cargas muy frecuentes.
    *   **Opción B (7 días):** Un estándar competitivo que ofrece una buena experiencia de usuario.
    *   **Opción C (14+ días):** Un diferenciador clave en el mercado, pero requiere una gestión de energía extremadamente optimizada y posiblemente una batería más grande.
*   **Impacto:** La respuesta a esta pregunta condiciona todo el diseño del firmware (la agresividad del "deep sleep"), el tamaño de la batería (y por tanto del dispositivo) y la frecuencia con la que se pueden enviar datos en tiempo real.