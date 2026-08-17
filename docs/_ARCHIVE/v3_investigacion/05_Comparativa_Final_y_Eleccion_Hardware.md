> **NOTA DE ACTUALIZACIÓN (Enero 2026):** Este documento forma parte del archivo de investigación. Las decisiones y componentes aquí analizados (ej. `Quectel BG96`, `MPU6050`) han sido superados. Para la especificación final y definitiva del hardware, por favor consulte **`docs/investigacion_tracker_diy/PRODUTO/Hardwear.txt` (v3.6)**, que establece la arquitectura modular basada en `LilyGo T-SIM7000G S3` y `BMI270`.

---

# 05 - Comparativa Final y Elección de Hardware para el Tracker ARES GPS

Este documento presenta una síntesis y un plan de acción basados en la investigación previa, enfocados en la selección de hardware asequible y de alta calidad para un tracker GPS comercializable en Europa. Se abordan las opciones desde la perspectiva de cumplir con requisitos de precisión (≤2m error ciudad/bosque), velocidad (0-30km/h acelerones), fiabilidad 24/7 y cumplimiento normativo (CE/GPSR 2026).

---

Para un GPS tracker de perros que busca la máxima precisión y fiabilidad en todos los entornos, la recomendación principal sigue siendo el **Nordic nRF9160 SiP** como base. Sin embargo, se presenta una comparativa detallada de alternativas asequibles para prototipado y validación de concepto sin sacrificar la calidad.

### Comparativa Opciones Asequibles (1ud, Alta Calidad, Precios 2026)

| Opción | Chip Base | Precisión GPS | Conectividad | Consumo (Sleep / TX) | Precio 1ud (€) | Sitio | CE-Ready |
|---|---|---|---|---|---|---|---|
| **1. Nordic nRF9160-DK** | nRF9160 SiP | <1-2m multibanda+A-GPS | LTE-M/BLE LR 1km | **2.7µA / ~18µA (eDRX)** | 45-60 | Mouser.es | Sí completo |
| **2. Walter (Vídeo)** | ESP32-S3 + Sequans Monarch 2 | 2-5m (single-band) | LTE-M/BLE/WiFi | **9.5µA / ~37µA** | 60-70 | Crowd Supply | Parcial |
| **3. Quectel BG96 + ESP32** | BG96 Cat-M1 | 1.5-2.5m GNSS | LTE-M/BLE/WiFi | **8-12µA** / Medio | 28-35 | AliExpress | Sí módulo |
| **4. RAK11720** | nRF52840 + LTE | 1-3m + IMU | LTE-M/NB/BLE | **6µA** / Medio | 35-45 | RAKwireless | Parcial |
| **5. LilyGO T-SIM7600E** | SIM7600 + ESP32 | 2m (GPS/GLONASS) | 4G/LTE/BLE/CAT-M | **15µA** / Alto | 22-30 | Amazon.es | Parcial |
| **6. Blues Notecard** | nRF9160 + SIM10a | <2m A-GPS | LTE-M global | **5µA** / Bajo | 55-65 | Blues.io | Sí completo |

*Nota sobre el consumo: "Sleep" se refiere al consumo en el modo de más bajo consumo (PSM/Deep Sleep). "TX" es una estimación del consumo durante la transmisión de datos; valores más bajos son significativamente mejores para la autonomía de la batería.*

**Ganador precio/calidad para prototipado rápido**: **Quectel BG96 + ESP32** (30€ total). Ofrece una precisión de 1.5m real, su módulo cuenta con certificación CE, y es fácil de programar con Arduino. Puede escalar a 15€/unidad en 100 unidades, lo que lo convierte en una opción ideal para validar el concepto sin una inversión inicial alta, manteniendo la calidad.

### Plantillas Hardware (Todas ≤110€/ud)

Estas plantillas ilustran posibles arquitecturas para el hardware, enfocándose en cómo cada una aborda el dilema de la **"Autonomía mínima realista"** y la **"Precisión"**.

#### Opción 1: nRF9160 Pro (95€)
```
[App EU (Flutter MQTT/BLE)] <--> nRF9160 (LTE-M global, BLE backup)
                               |
          GNSS Multibanda (≤2m garantizado) + A-GPS cloud
                               |
                I2C --> BMA400 IMU (actividad low-power 1µA)
                               |
     LiPo 1500mAh + PCM + Qi (carga sin puerto)
```
*   **Ventajas**: Mínimo tamaño (10x16mm), **batería para más de 15 días** de tracking continuo. Aborda la "Autonomía mínima realista" con creces y garantiza una precisión superior para entornos complejos.

#### Opción 2: Quectel BG96 DIY (35€)
```
ESP32 --UART--> BG96 GNSS/LTE --I2C--> MPU6050
       |
     BLE/WiFi backup
```
*   **Ventajas**: Ultra-barato y fácil de montar en protoboard, con librerías de Arduino listas. Una excelente opción para la validación inicial del concepto.

#### Opción 3: LilyGO Todo-en-Uno (28€)
```
T-SIM7600E (GPS+4G+BLE integrado)
   + IMU externo 2€
```
*   **Ventajas**: Solución "Plug & play" con disponibilidad rápida en Amazon. Ideal para pruebas rápidas de concepto.

### Costos Exactos y Escalado

| Cantidad | nRF9160 | Quectel+ESP32 | LilyGO |
|---|---|---|---|
| **1ud** | 95€ | 35€ | 28€ |
| **10ud** | 75€/u | 28€/u | 24€/u |
| **100ud** | 45€/u | 18€/u | 16€/u |
| **1000ud** | 32€/u | 12€/u | 11€/u |

*Nota: El envío a Palma puede añadir entre 8-15€ para la primera unidad.*

### Cómo Elegir Según Tu Prioridad

Esta sección vincula las opciones de hardware con las preguntas de diseño fundamentales:

-   **Máxima precisión/ciudad (≤2m)**: nRF9160 (multibanda+A-GPS). Responde al dilema de "¿Debe funcionar cuando NO hay cobertura móvil?" en el sentido de precisión urbana.
-   **Más barato posible (sin perder calidad)**: **Quectel BG96** (1.5m real, 35€). Ideal para validar el concepto de bajo coste.
-   **Más fácil empezar YA**: **LilyGO T-SIM7600E** (28€, stock en Amazon.es). Para una prueba de concepto rápida.
-   **Producto comercial Europa**: nRF9160 o Blues Notecard (pre-certificados). Aborda la legalidad y certificaciones necesarias.

### Pasos Inmediatos (Empieza Hoy)

1.  **Prototipo de 35€**: Compra un "Quectel BG96 ESP32" en AliExpress + un sensor MPU6050. Esto te permitirá responder a la pregunta de "Autonomía mínima realista" en un entorno real.
2.  **Prueba de 24h**: Programa un sketch de Arduino que envíe `{lat, lon, vel, accel}` por BLE cada 10 segundos.
3.  **Valida Precisión**: Camina y corre por ciudad/bosque midiendo el error de la traza contra Google Maps. Esto validará la precisión para el dilema "¿Debe funcionar cuando NO hay cobertura móvil?" en diferentes entornos.
4.  **Escala**: Si los resultados son satisfactorios, diseña y pide 10 unidades de una PCB custom en JLCPCB (coste aproximado 200€).

**Recomendación final**: Comienza con **Quectel BG96 (35€)** para validar el concepto. Si cumple con la precisión de 2m requerida, migra al **nRF9160** para la producción final. Esto te da calidad profesional a un precio de entrada de "maker".