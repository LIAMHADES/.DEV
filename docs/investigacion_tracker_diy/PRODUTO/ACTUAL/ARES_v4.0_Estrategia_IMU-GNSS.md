# ARES v4.0 — Actividad inteligente, ahorro de batería y precisión (IMU + GNSS + App)

## 0) Objetivo

Construir un tracker que:

* **Mida actividad fiable** (pasos/cadencia/intensidad) aunque el perro haga bucles y vuelva al mismo punto.
* **Ahorre batería** reduciendo GNSS/LTE cuando no aporta valor.
* Mantenga **seguridad y confianza**: geofence y LOST sin “cegar” alertas.
* Sea competitivo: LIVE rápido cuando el usuario lo pide, y modo normal eficiente.

---

## 1) Cambio clave respecto a enfoques anteriores

### Antes (riesgo)

* Dependencia excesiva de **GNSS con baja frecuencia** → si el perro hace bucles, puede parecer que “no se movió” o que fue lento.
* Envíos de posición demasiado frecuentes → consumo alto, especialmente en mala cobertura.

### Ahora (v4.0 inteligente)

* **IMU como sensor primario de locomoción** (actividad en continuo) + **GNSS como ancla/corrección**.
* Envíos **event-driven** (por riesgo/eventos) + **batch** de métricas de actividad.
* Integración con app para activar **LIVE** solo cuando aporta valor.

---

## 2) Arquitectura funcional: “Locomoción primero”

### 2.1 IMU (actividad) → calcula en local

El dispositivo estima continuamente (por ventanas de 2–5 s):

* **Pasos / zancadas** (conteo)
* **Cadencia** (pasos/min)
* **Intensidad / energía** (score 0–100)
* **Eventos**: cambio fuerte de dirección, sprint, paradas, caídas.

### 2.2 GNSS (posicionamiento) → ancla y valida

GNSS se usa para:

* **Calibrar longitud de zancada** por perro (walk/trot/run)
* **Corregir deriva** a largo plazo
* Generar track cuando el usuario lo necesita (**LIVE**)
* Validar coherencia (si GNSS dice casi parado y la IMU “da pasos”, se filtra como falso)

### 2.3 Resultado

Aunque el perro vuelva al mismo punto:

* La **distancia por locomoción** sigue sumando.
* GNSS solo corrige y ancla.

---

## 3) Scheduler de posicionamiento (IMU-driven)

El firmware usa una **máquina de estados**. La IMU gobierna cuándo activar GNSS y cuánto enviar.

### Estados recomendados (base)

* **REST**: sin locomoción

  * GNSS casi siempre OFF
  * Envío heartbeat cada **10–30 min** (batería/estado/calidad)
* **WALK**: locomoción baja/estable

  * GNSS cada **30–60 s**
  * IMU: pasos/cadencia/intensidad en continuo
* **RUN**: alta cadencia/alta energía

  * GNSS cada **5–10 s**
* **LIVE** (usuario mirando mapa)

  * GNSS cada **2–3 s**
* **LOST**

  * No “2 s siempre” por defecto.
  * **Ráfagas** de 2–3 s cuando hay riesgo (geofence cerca, aceleración alta, usuario activo)
  * Escalado dinámico si no hay riesgo.

### Envíos event-driven (disparadores)

Aunque estés en WALK/REST, envías antes si:

* Cambio fuerte de dirección
* Sprint
* Geofence “near boundary”
* Degradación de calidad GNSS (para evitar track falso)

---

## 4) Métricas que se guardan y se envían en batch

En vez de enviar GNSS todo el rato, el dispositivo acumula (por minuto):

* pasos/zancadas
* cadencia media y máxima
* tiempo en REST/WALK/TROT/RUN
* intensidad 0–100
* conteo de giros fuertes y sprints
* calidad de señal (GNSS/LTE) y flags de confianza

En cada envío GNSS (o cada X minutos) se adjunta:

* “resumen de actividad” + último fix GNSS

---

## 5) Antifallos: evitar falsos pasos (sacudidas/rascado)

### Problema

Sacudidas/rascado generan aceleraciones altas que pueden parecer pasos.

### Solución

* Clasificador de actividad por features IMU (energía, frecuencia dominante, ratio gyro/acc, jerk)
* Reglas anti-shake:

  * jerk muy alto + patrón no periódico → no locomoción
* Validación cruzada:

  * si GNSS indica casi parado y hay pasos, se descartan

---

## 6) Personalización por perro (aprendizaje)

### Calibración inicial

Durante sesiones con GNSS bueno (o LIVE):

* se estima longitud de zancada para walk/trot/run
* se aprende relación cadencia→velocidad

### Ajuste por backend

* Ajuste por tamaño/peso/raza
* Corrección por histórico del perro (patrón típico)

Resultado: mejor clasificación y conteo más estable.

---

## 7) Integración con la app: ahorrar usando el móvil como sensor auxiliar

### Idea

Cuando el móvil está cerca (<2 m) por BLE:

* el collar puede bajar GNSS
* el móvil aporta contexto (ruta/velocidad) si el usuario da permisos

### Regla crítica

**No depender de “pasos del móvil” como verdad.** El móvil puede estar en bolso, bici, coche, etc.

### Modo “Phone-Assist” (auxiliar)

Se activa solo si:

* BLE RSSI indica cercanía estable (<2 m) durante N segundos
* IMU del perro indica locomoción
* el móvil reporta **movimiento fiable** (GPS speed / actividad), no solo pasos

Ahorro:

* GNSS del collar baja a 60–120 s
* actividad del perro sigue por IMU
* track se reconstruye con ruta del móvil + anclas del collar

Fail-safe:

* si RSSI cae o móvil no es fiable → volver a scheduler normal
* geofence/LOST nunca dependen del móvil

---

## 8) Cuellos de botella (los problemas principales a resolver)

1. **Energía / picos LTE en mala cobertura**

   * si hay caídas de VBAT → resets → reintentos → consumo disparado
2. **RF real en carcasa IP68**

   * detuning de antenas + ruido de reguladores afecta GNSS

Orden de consumo típico:

1. LTE TX + reintentos
2. GNSS continuo
3. LEDs
4. MCU + IMU

---

## 9) Implicaciones de hardware (lo que cambia / lo que hay que añadir)

### Cambios mínimos obligatorios

* IMU adecuada para:

  * detección de locomoción
  * eventos (giros, sprints)
  * bajo consumo
* Telemetría de batería/energía:

  * medición de corriente (o al menos VBAT estable)
* RF:

  * colocación de antenas LTE + GNSS + keep-out
  * red de matching (DNP al inicio) para tuning en carcasa

### Cosas que suelen faltar y aquí se vuelven obligatorias

* estrategia anti-brownout (hardware + firmware)
* batch store&forward de métricas
* flags de “confianza” de actividad y posicionamiento

---

## 10) Plan de validación mínimo (banco + campo)

### Banco (1 tarde)

* Medir consumo por estado: REST/WALK/RUN/LIVE/LOST
* Validar picos LTE y caída de VBAT
* Validar que GNSS no se degrada cuando LTE transmite

### Campo (1 día)

3 escenarios (≥20 min cada uno):

* open sky
* urbano cañón
* bosque/parque frondoso

Registrar:

* TTFF
* precisión p50/p90/p95
* outliers (saltos)
* coherencia pasos/cadencia vs anclas GNSS

Criterio de éxito (prototipo):

* actividad coherente (sin falsos pasos masivos)
* ahorro real medible al bajar frecuencia GNSS/LTE
* LIVE estable (2–3 s) cuando el usuario lo activa

---

## 11) Decisiones actuales y pendientes

### Decidido (v4.0)

* Actividad por IMU + GNSS como ancla
* Scheduler IMU-driven
* Batch de métricas + event-driven triggers
* Phone-Assist como modo auxiliar (no dependencia)

### Pendiente de cerrar

* IMU final (modelo exacto)
* Umbrales por estado (WALK/RUN/LOST)
* Política exacta de ráfagas en LOST
* Modelo de personalización por raza/tamaño

---

## 12) Summary para producto (mensaje claro)

ARES registra la actividad de forma fiable incluso si el perro hace bucles, porque no depende solo del GPS: usa sensores de movimiento para medir pasos y esfuerzo. El GPS se enciende cuando aporta valor (seguridad o mapa en vivo), ahorrando batería sin perder control. Cuando el dueño está cerca, el móvil puede ayudar como sensor auxiliar, pero el collar sigue siendo la fuente de verdad.
