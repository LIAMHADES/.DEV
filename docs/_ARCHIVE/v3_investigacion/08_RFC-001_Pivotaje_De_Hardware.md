> **NOTA DE ACTUALIZACIÓN (Enero 2026):** Este documento forma parte del archivo de investigación. Las decisiones y componentes aquí analizados (ej. `Quectel BG96`, `MPU6050`) han sido superados. Para la especificación final y definitiva del hardware, por favor consulte **`docs/investigacion_tracker_diy/PRODUTO/Hardwear.txt` (v3.6)**, que establece la arquitectura modular basada en `LilyGo T-SIM7000G S3` y `BMI270`.

---

## Análisis Crítico: Lo Guardado vs. Lo que Falta

Tu proyecto actual tiene un Ferrari de software (un backend FastAPI bien estructurado, una base de datos con lógica de negocio canina, un frontend React) pero está intentando funcionar con el motor de un cortacésped (un hardware genérico que no cumple los requisitos mínimos).

Lo que SÍ está en la carpeta (y es valioso):

1.  Backend Robusto (`app/`): Tienes una API con endpoints, configuración de base de datos (database.py), modelos (models.py) y rutas (routes/). Esto es una base excelente y reutilizable casi al 100%.
2.  Base de Conocimiento (`docs/knowledge_base`): Has recopilado información sobre nutrición, ejercicio e IMC canino. Esto es el "cerebro" de la lógica de negocio y es fundamental.
3.  Frontend (`frontend/`): Tienes una aplicación de visualización lista para mostrar los datos, lo cual te ahorra mucho tiempo.

Lo que se ha dejado fuera (y es CRÍTICO):

Basándome en tus propios documentos (`documento_completo_de_proyecto_GPS.md`), he identificado los siguientes puntos de fallo que la información del vídeo soluciona:

1.  **EL HARDWARE NO ES UN GPS REAL**: Tu plan menciona el uso de un dispositivo genérico (similar al GF-07). Estos dispositivos NO usan GPS; usan LBS (triangulación de antenas 2G).
    *   **Consecuencia**: La precisión es de 500 a 1000 metros. Es imposible saber si el perro está en el jardín o cruzando la autopista. Todo tu sistema de geovallas es inútil con este hardware.

2.  **LA COMUNICACIÓN ES LENTA Y CARA**: Tu arquitectura se basa en recibir SMS y parsearlos (`app/routes/sms.py`).
    *   **Consecuencia**: Los SMS tienen latencia, cuestan dinero por cada mensaje y dependen de que un móvil intermedio esté siempre encendido y con cobertura. Esto no es escalable ni fiable para un producto.

3.  **FALTA MEDICIÓN DE ACTIVIDAD REAL**: Tu sistema calcula calorías por la distancia recorrida (obtenida del LBS, que ya es impreciso).
    *   **Consecuencia**: No puedes saber si el perro ha estado durmiendo todo el día o jugando intensamente en el mismo sitio. Te falta un Acelerómetro (IMU) para medir la actividad real, un componente clave mencionado en el análisis avanzado.

## Documento de Pivotaje: El Plan para Arreglarlo

Para que tu proyecto ARES sea viable, necesitas adoptar la tecnología analizada. He creado un documento formal de "Request for Change" (RFC) que especifica exactamente qué cambiar. Puedes guardar esto como `docs/investigacion_tracker_diy/08_RFC-001_Pivotaje_De_Hardware.md`.

---

# ARES GPS: Documento de Pivotaje de Hardware y Arquitectura (RFC-001)

**Fecha:** 10 de Enero, 2026
**Estado:** CRÍTICO / APROBADO
**Objetivo:** Migración de tecnología GF-07 (SMS/LBS) a Hardware IoT Profesional (GNSS/LTE-M).

## 1. Resumen Ejecutivo (El Problema)

Hemos determinado que la arquitectura actual basada en el dispositivo **GF-07** y la pasarela de SMS vía Android es **inviable** para cumplir con la misión del proyecto ARES.

Las pruebas y el análisis técnico han revelado fallos estructurales insalvables:
1.  **Falsa Precisión:** El GF-07 no usa GPS real (satélites), sino LBS (triangulación de antenas 2G). El margen de error es de 500m a 1km. Es imposible calcular geovallas o actividad física real.
2.  **Latencia Inaceptable:** El uso de SMS introduce retrasos de segundos a minutos. No permite rastrear un perro en movimiento (0-45 km/h).
3.  **Dependencia Frágil:** El sistema actual depende de que un móvil Android intermedio tenga batería, cobertura y la app activa para reenviar los datos al servidor.

**Decisión:** Se cancela el desarrollo sobre GF-07. Se migra a hardware IoT con **GNSS Real** y conectividad **LTE-M directa** (Estilo Placa Walter / Nordic nRF9160).

## 2. Nueva Arquitectura de Sistema

Pasamos de una arquitectura "Mediadas por Humano/SMS" a una arquitectura **"IoT Direct-to-Cloud"**.

### Arquitectura ANTERIOR (OBSOLETA - DEPRECATED)
`[GF-07] --(SMS 2G)--> [Móvil Android Usuario] --(App Puente)--> [API ARES /sms]`
*   *Fallo:* Cuello de botella en el móvil, coste por SMS, datos LBS imprecisos.

### Arquitectura NUEVA (TARGET)
`[Hardware ARES (ESP32+Sequans/Nordic)] --(Datos LTE-M)--> [1NCE Network] --(HTTP/MQTT)--> [API ARES /data]`
*   *Ventaja:* Conexión directa, tiempo real (<200ms), GPS de precisión (<5m), coste fijo (10€/10 años).

## 3. Especificaciones de Cambios en el Código (Backend & Frontend)

### 3.1. Qué debemos ELIMINAR o MARCAR COMO OBSOLETO
El desarrollador debe congelar o eliminar los siguientes componentes:

*   ❌ **Endpoint `/sms`:** La lógica de parseo de texto de SMS (buscar "google maps links") ya no es necesaria.
*   ❌ **Android Gateway Script:** La automatización de envío de coordenadas desde el móvil Android se cancela. El móvil ya no es un sensor, es solo un visualizador (Cliente).
*   ❌ **Tablas de `sms_inbox`:** Ya no almacenaremos SMS crudos.

### 3.2. Qué debemos IMPLEMENTAR (Nuevos Requisitos)

#### A. Nuevo Endpoint de Ingesta de Datos (`/api/v1/ingest`)
El dispositivo enviará un payload JSON (o binario optimizado) directamente vía HTTP POST o MQTT.
**Estructura de Datos Esperada:**
```json
{
  "device_id": "imei_123456789",
  "timestamp": 1704892200,
  "gps": {
    "lat": 40.416775,
    "lon": -3.703790,
    "accuracy": 2.5,      // Precisión en metros (Vital para filtrar "ruido")
    "satellites": 8       // Nº de satélites (Calidad de señal)
  },
  "telemetry": {
    "battery_mv": 3800,   // Voltaje real (para calcular %)
    "temperature": 36.5,  // Temperatura interna del collar
    "activity_score": 150 // Dato del acelerómetro (Nuevo componente)
  },
  "status": "MOVING"      // MOVING, STATIC, CHARGING
}
```

#### B. Lógica de "Store & Forward" (Gestión de Zonas Muertas)
El backend debe estar preparado para recibir **arrays de puntos**.
*   *Escenario:* El perro entra en un bosque sin cobertura LTE. El collar guarda 50 puntos GPS. Al recuperar señal, envía un solo paquete con los 50 puntos históricos.
*   *Acción Dev:* La API debe procesar listas de coordenadas con timestamps pasados, no solo el "ahora".

#### C. Integración de Actividad (El "Nichols Score")
El cálculo de calorías ya no se basará solo en "distancia GPS" (que es imprecisa).
*   **Nuevo Input:** El hardware incluirá un **Acelerómetro (IMU)**.
*   **Lógica:** `Calorías = (Factor Raza * Peso) + (Datos GPS Distancia) + (Datos IMU Intensidad)`.
*   El backend debe almacenar este valor de "intensidad" o "pasos" en la tabla `activity_daily`.

## 4. Requisitos de Hardware (Para referencia del Dev)

El software debe escribirse asumiendo que el hardware tendrá las siguientes capacidades (basadas en el análisis del vídeo de la placa Walter):

1.  **Conectividad:** LTE-M (Datos móviles IoT). No WiFi (salvo para backup en casa).
2.  **Energía:** El dispositivo duerme el 99% del tiempo. Solo despierta si el acelerómetro detecta movimiento real.
3.  **GPS Cold Start:** El dispositivo puede tardar hasta 40s en enviar la primera posición al salir de casa. El frontend debe mostrar un estado de "Buscando satélites...".
4.  **Actualizaciones OTA:** El ESP32 permite actualizaciones de firmware por aire. Necesitaremos un endpoint en el futuro para servir los binarios de actualización.

## 5. Plan de Acción Inmediato

1.  **Stop:** Detener desarrollo de parseo de SMS.
2.  **Refactor DB:** Adaptar la tabla `locations` para incluir campos de `accuracy` (precisión), `battery_voltage` y `activity_index`.
3.  **Mocking:** Crear un script en Python que simule ser el nuevo dispositivo (Hardware ARES) enviando peticiones JSON al nuevo endpoint, para poder probar el Frontend y la lógica de calorías sin tener el hardware físico todavía.

---
*Este documento invalida las especificaciones anteriores relacionadas con GF-07 y mensajería SMS.*