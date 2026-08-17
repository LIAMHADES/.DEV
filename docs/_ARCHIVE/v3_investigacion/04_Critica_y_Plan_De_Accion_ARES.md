> **NOTA DE ACTUALIZACIÓN (Enero 2026):** Este documento forma parte del archivo de investigación. Las decisiones y componentes aquí analizados (ej. `Quectel BG96`, `MPU6050`) han sido superados. Para la especificación final y definitiva del hardware, por favor consulte **`docs/investigacion_tracker_diy/PRODUTO/Hardwear.txt` (v3.6)**, que establece la arquitectura modular basada en `LilyGo T-SIM7000G S3` y `BMI270`.

---

# 04 - Análisis Crítico del Proyecto ARES GPS Actual y Plan de Acción

Este documento es una evaluación crítica del proyecto ARES GPS en su estado actual, cruzado con la información de la investigación de hardware. El objetivo es identificar puntos de fallo y proponer un plan de acción concreto para pivotar hacia una arquitectura viable y profesional.

---

### 1. El Punto de Fallo Crítico: El Dispositivo GF-07

El plan inicial de ARES mencionaba el uso del **GF-07**. Este dispositivo representa el principal problema del proyecto, ya que su capacidad es fundamentalmente incompatible con los objetivos de precisión y fiabilidad.

*   **Realidad:** El GF-07 **NO TIENE GPS REAL**. Funciona por **LBS (Location Based Service)**, triangulando antenas de telefonía 2G.
*   **Consecuencias Directas:**
    *   **Precisión Nula:** El error es de 500 a 1000 metros. Esto hace imposible usar las geovallas de forma fiable (ej. no se puede saber si el perro está en el jardín o cruzando la autopista) o calcular distancias recorridas con exactitud para la lógica de salud.
    *   **Red Obsoleta:** La red 2G (GPRS) está siendo desmantelada progresivamente en muchos países, comprometiendo la viabilidad a medio y largo plazo.
*   **Conclusión:** El software de alta precisión de ARES no puede funcionar con los datos de baja calidad del GF-07. **Es imperativo cambiar el hardware a un módulo con GNSS real.**

### 2. Arquitectura de Comunicación: SMS vs. Datos (MQTT/HTTP)

El flujo de comunicación actual de ARES (`Dispositivo -> SMS -> Móvil Android -> API`) es inherentemente frágil e ineficiente.

*   **Problemas:**
    *   **Latencia y Coste:** Los SMS no son en tiempo real y suelen tener un coste por unidad, haciendo que un seguimiento frecuente sea económicamente inviable. Esto impacta directamente en el dilema de **"¿Necesitas comandos downlink de verdad?"** y la capacidad de obtener una ubicación rápidamente.
    *   **Punto de Fallo Único:** El sistema depende completamente de que el móvil Android intermediario tenga batería, cobertura y la app funcionando correctamente como puente. Esto introduce un punto de fallo crítico fuera de nuestro control.
*   **Solución Propuesta:** El dispositivo debe usar su propia SIM de datos (**1NCE** u otra solución IoT) para conectarse a Internet (**LTE-M**) y enviar los datos directamente a la API de ARES (vía HTTP o MQTT), sin intermediarios. Esto aborda el dilema de **"¿SIM del usuario o SIM tuya (suscripción)?"** optando por una SIM incluida para una mejor UX y fiabilidad.

### 3. Carencia en "Salud y Nutrición": Falta de un Acelerómetro (IMU)

El cálculo de calorías de ARES se basa en la "distancia recorrida" del GPS (LBS), lo cual es impreciso y energéticamente ineficiente.

*   **El Fallo:** No se puede tener el GPS encendido todo el día por su alto consumo, y el GPS no distingue entre un perro corriendo o uno durmiendo en el mismo sitio.
*   **Lo que falta:** Un **Acelerómetro (IMU)** para medir el nivel de actividad real de forma eficiente y despertar al GPS solo cuando sea necesario. Esto es clave para lograr una **"Autonomía mínima realista"** y obtener datos precisos para la lógica de salud.

---

### Comparativa: Tu Plan Actual (ARES) vs. Producto Viable (PRO)

| Característica | Plan Actual (ARES / GF-07) | Producto Viable (Estilo Walter/Nordic) |
| :--- | :--- | :--- |
| **Tecnología Ubicación** | LBS (Error >500m) | **GNSS Real (Error <5m)** |
| **Funcionamiento sin Cobertura Móvil** | No aplica | **Potencialmente con respaldo LoRa/BLE LR** (Responde a "¿Debe funcionar cuando NO hay cobertura móvil?") |
| **Comunicación** | SMS (Caro, Lento, Inseguro) | **Datos LTE-M (Barato, Rápido, Fiable)** |
| **Batería** | 1-2 días (Sin gestión inteligente) | **Semanas/Meses (con Deep Sleep y IMU)** (Responde a "Autonomía mínima realista") |
| **Detección de Actividad** | Estimada (Imprecisa) | **Real (con IMU)** |
| **Resistencia al agua** | Ninguna | **IP67/68 (con diseño adecuado)** |
| **SIM** | N/A (implícitamente la del usuario para SMS) | **Incluida (1NCE/Blues)** (Responde a "¿SIM del usuario o SIM tuya?") |

---

### Resumen del Plan de Acción

El backend y frontend de ARES son un **excelente motor de Ferrari**, pero actualmente están intentando funcionar con el chasis y motor de un **cortacésped** (GF-07 y la arquitectura de SMS).

**Pasos Obligatorios para ARES para un Pivotaje Exitoso:**

1.  **Sustituir el Hardware:** Descartar el GF-07. Adoptar una placa con **GPS Real + LTE-M** (ej. Quectel BG96 + ESP32 para empezar) y un **IMU** integrado.
2.  **Modificar la API:** Adaptar el endpoint `/sms/inbound` para que acepte datos en formato JSON/MQTT directamente desde el nuevo dispositivo, o crear un nuevo endpoint `/api/v1/ingest` como se detalla en el RFC-001.
3.  **Integrar el IMU:** Añadir el acelerómetro al plan de hardware y la lógica de "actividad" al firmware para alimentar correctamente la base de datos de salud canina y gestionar el Deep Sleep.
4.  **Considerar Comandos Downlink:** Definir si la arquitectura del backend y el firmware deben soportar comandos desde la app al dispositivo ("¿Necesitas comandos downlink de verdad?").
