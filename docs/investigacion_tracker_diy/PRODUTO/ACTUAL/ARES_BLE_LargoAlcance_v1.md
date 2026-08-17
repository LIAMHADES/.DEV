# ARES — Bluetooth de Largo Alcance (BLE Long Range) como vía de respaldo sin internet

**Versión:** 1.0 (borrador de investigación) | **Estado:** PENDIENTE DE VALIDACIÓN con ingeniería de hardware y desarrollo de app
**Fecha:** 2026-07-29
**Autor:** Claude (a petición de Liam)

> [ATENCION]  Este documento es una investigación inicial para decidir SI implementar un modo de comunicación directa collar↔móvil por Bluetooth de largo alcance, útil cuando el usuario **no tiene datos móviles** (zonas remotas, extranjero sin roaming, sin cobertura). NADA aquí está confirmado como viable hasta validar los 3 puntos de la sección 5. No comunicar en marketing/web hasta entonces.

---

## 1. El problema que resolvería

Hoy ARES reporta la ubicación **solo** a través de su propia red móvil (LTE) → nube → app. Esto falla en un caso concreto:

- **El usuario está en una zona remota sin cobertura móvil en su propio teléfono** (montaña, extranjero sin datos, pueblo sin señal), y necesita saber dónde está su perro AHORA, cerca de él.

En ese escenario, aunque el collar siga funcionando, el dueño no puede consultar la nube porque su móvil no tiene internet. Un **enlace Bluetooth directo collar↔móvil**, que no dependa de internet en ninguno de los dos lados, cubriría exactamente ese hueco: el móvil se conecta directamente al collar por BLE y lee su posición/dirección sin pasar por la red.

Valor comercial: es un diferenciador real ("funciona aunque te quedes sin datos") que ataca un miedo concreto del dueño outdoor. Ningún competidor analizado lo destaca.

---

## 2. La tecnología: BLE Long Range (Coded PHY)

- **BLE clásico (1M PHY):** alcance práctico ~10-30 m en interior, hasta ~50 m en línea de visión. Es lo que ARES usa hoy para "Phone-Assist" y búsqueda de cercanía.
- **BLE Long Range (Coded PHY, S=8), introducido en Bluetooth 5.0:** sacrifica velocidad de datos por alcance. En **campo abierto y línea de visión directa** puede alcanzar **200 m – 1 km**; en condiciones reales con obstáculos (árboles, cuerpo del perro, desnivel) baja a **100-300 m**. Para transmitir una coordenada GPS (pocos bytes) la baja velocidad no es problema.

**Cifra honesta a comunicar si se implementa:** "hasta ~100 m en campo abierto" — nunca una cifra fija, porque el alcance real depende del entorno.

---

## 3. ¿El hardware actual lo soporta? (lo más importante)

El chip principal de ARES es el **LilyGo T-SIM7000G S3**:
- El **"S3" = ESP32-S3** (el microcontrolador de la placa). El ESP32-S3 **soporta Bluetooth 5.0 LE, incluido Coded PHY (Long Range)** a nivel de silicio. Fuente: datasheet oficial de Espressif ESP32-S3 (soporte BLE 5.0 con Long Range / 2 Mbps / Extended Advertising).
- El **módulo SIM7000G** aporta GNSS + LTE, NO el Bluetooth. El BLE viene del ESP32-S3.

**Conclusión preliminar (a validar):** es MUY probable que **no haga falta comprar un chip nuevo** — el ESP32-S3 ya presente en el diseño soporta BLE Long Range. El coste incremental de hardware sería **cercano a 0€** si:
1. La antena BLE actual del diseño tiene ganancia suficiente (una antena mejor podría costar 0,5-2€).
2. El firmware se programa para activar Coded PHY en el modo de respaldo.

Es decir: **potencialmente es coste de FIRMWARE + posible ajuste de antena, no de un componente caro nuevo.** Esto lo convierte en una funcionalidad muy rentable de añadir (alto valor percibido, coste marginal casi nulo) — SI se confirman los 3 puntos de la sección 5.

---

## 4. Coste estimado

| Concepto | Coste incremental estimado | Nota |
|---|---|---|
| Chip BLE nuevo | **0€** (probable) | El ESP32-S3 ya soporta Coded PHY |
| Antena BLE mejorada (opcional) | 0,5 – 2€ | Solo si la antena actual no da alcance |
| Firmware (modo respaldo BLE) | 0€ material (horas de desarrollo) | Coste en tiempo de ingeniería, no en BOM |
| Desarrollo app (soporte Coded PHY) | 0€ material (horas de desarrollo) | Ver riesgo en §5 |
| **Total incremental BOM** | **~0 – 2€** | Frente a los ~64-67€ de BOM actual, es despreciable |

El coste real no es de materiales, es de **horas de desarrollo de firmware + app**.

---

## 5. Los 3 puntos que HAY que validar antes de prometer nada

1. **¿La antena BLE del diseño actual da alcance suficiente en Coded PHY?**
   - Requiere prueba de banco real. La huella de antena del PCB actual (Ignion A101 es para GPS/LTE; el BLE del ESP32-S3 usa su propia antena/traza) debe evaluarse. Puede que necesite una antena BLE dedicada o mejor situada.

2. **¿Los móviles de los usuarios soportan BLE Long Range (Coded PHY)?** ← EL CUELLO DE BOTELLA REAL
   - Coded PHY requiere que el HARDWARE Bluetooth del móvil lo soporte, no solo Android/iOS.
   - Muchos móviles de gama media/baja **NO** exponen Coded PHY aunque tengan "Bluetooth 5.0". iPhone lo soporta desde modelos recientes; en Android es muy fragmentado.
   - **Consecuencia:** en móviles sin Coded PHY, el enlace caería al BLE normal (~30-50m), no a los 100m. Hay que comunicarlo con esa salvedad, o el usuario se sentirá engañado.

3. **¿La app puede implementar y mantener este modo?**
   - Requiere desarrollo específico: detectar "sin internet" → ofrecer modo directo → escanear/conectar por BLE Long Range → mostrar dirección/distancia (tipo "frío/caliente", ya que la coordenada suelta sin mapa cargado sirve de poco sin internet para el mapa).
   - Ojo: sin internet, la app tampoco puede cargar mapas online. El modo BLE mostraría dirección + distancia (brújula), no un mapa — hay que diseñar esa UX.

---

## 6. Recomendación

**Merece la pena investigarlo en serio** porque el coste de hardware es casi nulo y el valor (funciona sin datos, en remoto) es alto y diferenciador. PERO:

- **NO comunicarlo en la web todavía.** Prometer "100m sin internet" sin validar los 3 puntos de §5 (sobre todo el soporte del móvil del usuario) contradice el tono de voz de ARES ("Datos > Opiniones", no vender magia).
- **Siguiente paso:** pasar los 3 puntos de validación al ingeniero de hardware (antena) y al desarrollador de app (soporte Coded PHY + UX sin internet). Con eso confirmado, se comunica como "hasta ~100m en campo abierto, con móviles compatibles".

---

## 7. Cómo se comunicaría (SI se valida) — borrador de copy

> **"Y si te quedas sin datos, sigues teniéndolo cerca"**
> En mitad de una ruta, sin cobertura en tu móvil, ARES no te deja tirado: se conecta directamente a tu teléfono por Bluetooth de largo alcance, sin necesitar internet ni el uno ni el otro. La app te guía hacia él hasta unos 100 metros en campo abierto. (Requiere un móvil compatible.)

Este copy queda EN ESPERA hasta validación.
