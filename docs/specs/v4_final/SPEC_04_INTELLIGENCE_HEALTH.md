# SPEC_04: Inteligencia, Salud y Explicabilidad (ARES v4.0)

**Objetivo**: Aportar valor añadido (Health/Activity) y reducir soporte técnico mediante transparencia (Explicabilidad).

**Nota de posicionamiento:** esta spec es el corazón técnico del eje de producto "salud/bienestar general del perro" (ver `01_PRODUCTO_Y_NEGOCIO.md` §1.5) — el diferenciador principal de ARES frente a la competencia no es el tracking en sí (terreno ya cubierto por todos los competidores analizados), sino la calidad de estos insights de salud.

## 1. Salud y Actividad (Sensor BMI270)

Transformar datos crudos de IMU en "Insights" de comportamiento.

### 1.1. Métricas Base

El dispositivo procesa internamente (Edge Computing) para no saturar el envío de datos:

- `steps`: Pasos detectados (pedometer).
- `activity_level`: Intensidad media (High/Med/Low) en el intervalo.
- `rest_time`: Minutos de inmovilidad total.

### 1.2. Detección de Anomalías (Backend)

- **Baseline Individual**: El servidor calcula la media de actividad del perro (ej. Lunes a Viernes vs Fines de Semana).
- **Alertas no médicas**:
  - "Hoy es un día muy tranquilo": -30% vs media.
  - "Noche inquieta": Muchos micropasos/despertares de 02:00 a 06:00.

### 1.3. Lógica ANTI-FRAUDE (Validación de Ranking)

- **Regla**: Si `GPS Speed > 20 km/h` Y `BMI270 Motion == STATIC/LOW` -> Es **TRANSPORTE (Coche/Moto)**.
- **Acción**: Ese tramo de distancia NO suma para leaderboards de "Gimnasio/Paseo", pero SÍ se registra como ruta. Etiquetar como `activity_mode = VEHICLE`.

## 1.4. Estimación de Esfuerzo/Frecuencia Cardíaca vía IMU (nuevo, v4.0 — alcance acotado)

**Contexto y decisión:** ARES no tiene ningún sensor biométrico dedicado (frecuencia cardíaca, respiración, HRV) — brecha confirmada frente a competidores como Tractive (estimación algorítmica vía IMU) e Invoxia (sensor dedicado). El usuario decidió explícitamente: **solo se implementa la estimación algorítmica vía IMU (replicando el enfoque de Tractive), sin añadir ningún sensor nuevo a la BOM.** Un sensor óptico dedicado (PPG, tipo MAX30102/MAX86141) queda **descartado por ahora** — "muy difícil de implementar y no necesario en este momento" — no se elimina del radar, pero no forma parte de esta versión. Ver Risk Register (`RR-004`) para el detalle de por qué se descarta y qué se perdería/ganaría si se retoma.

### 1.4.1. Qué se mide y cómo
- **Fuente de datos:** el mismo BMI270 (IMU) ya presente en la BOM — sin sensor adicional, sin coste marginal de hardware.
- **Principio:** durante el estado `REST` confirmado (sin locomoción, inmovilidad prolongada), el micro-movimiento residual capturado por el acelerómetro de alta sensibilidad puede correlacionarse con el ciclo respiratorio y, en menor medida, con el pulso — el mismo principio que usa Tractive para estimar frecuencia cardíaca/respiratoria sin sensor dedicado.
- **Salida:** una **estimación de esfuerzo/frecuencia** (respiración en reposo como proxy principal, más fiable que el pulso por esta vía indirecta), nunca presentada como medición clínica. Etiquetar siempre como "estimación" en la app y en cualquier documento de cara al usuario.
- **Baseline individual:** igual que en §1.2, el backend calcula una línea base por perro (p. ej. frecuencia respiratoria media en reposo nocturno) y genera alertas no médicas ante desviaciones ("hoy respira más rápido de lo habitual en reposo"), reutilizando el mismo pipeline de detección de anomalías ya descrito.

### 1.4.2. Restricciones de coste (batería y datos) — validado contra el modelo de consumo

Antes de dar esta estimación por buena, se validó contra el modelo de consumo de `ARES_Analisis_Red_y_Consumo_v1.md`:
- **Batería:** el coste marginal es el de un muestreo de IMU más frecuente/sensible durante REST (hoy el IMU en REST solo confirma "sin locomoción" a baja frecuencia). Este muestreo adicional no requiere activar GNSS ni módem — el impacto en batería es mucho menor que cualquier fase con GNSS activo (WALK/RUN/LIVE), pero no es cero: **queda pendiente de medición de banco real** cuánto añade un muestreo continuo de IMU en alta resolución durante las horas de REST (típicamente 8h/día).
- **Datos:** el campo nuevo en el payload (`resp_rate_est` o similar, enviado solo en el heartbeat de REST, cada 10-30 min) es de unos pocos bytes — impacto insignificante sobre el presupuesto de ~250MB/mes ya con amplio margen (ver análisis de red, consumo real proyectado ~1,4MB/mes en patrón típico).
- **Conclusión:** viable dentro del presupuesto de datos sin ninguna duda; el punto a validar en campo es exclusivamente el coste en batería del muestreo de IMU más fino durante REST, no el envío del dato en sí.

### 1.4.3. Qué NO se hace en esta versión
- No hay sensor de contacto con la piel, no hay medición directa de pulso, no hay SpO2, no hay HRV real.
- No se presenta ningún claim de "frecuencia cardíaca exacta" en marketing — solo "estimación de frecuencia respiratoria en reposo" o equivalente, mientras no exista un sensor dedicado que lo respalde.
- La landing page y materiales de marketing deben evitar el mismo error ya corregido para "calidad del sueño" (ver `landing/index.html`): no prometer más de lo que el algoritmo realmente entrega.

## 2. Explicabilidad de Batería/Cobertura

Sistema para responder "¿Por qué se gastó la batería?" sin intervención humana.

### 2.1. Contadores Internos (Firmware)

El dispositivo mantiene contadores "desde última carga completa":

- `time_searching_net`: Segundos buscando cobertura (el mayor costo).
- `time_gps_fix`: Segundos con GPS encendido intentando fijar.
- `led_usage`: Segundos con luces encendidas.
- `live_mode_usage`: Segundos en modo Live (alta frecuencia).

### 2.2. Reporte de Sesión

Al enviar un paquete de estado (o al detectar carga), envía estos contadores.

### 2.3. Interpretación (Usuario)

El Backend procesa los contadores y genera mensajes "Humanos" en la App:

- **"Consumo elevado hoy por: Mala Cobertura"**: Si `time_searching_net` es alto. _Acción: "Intenta evitar zonas de sombra si es posible"._
- **"Consumo elevado hoy por: Luces"**: Si `led_usage` es alto.
- **"Consumo Normal"**: Si está en rangos esperados.
  Esto educa al usuario y evita tickets de "Batería defectuosa".
