# ARES v4.0 — Análisis de Proveedor de Red, Flujo de Datos y Consumo por Fase de Actividad
**Versión:** 1.0 | **Estado:** Final | **Motivo:** el usuario pidió verificar en vivo si el proveedor de SIM/red referenciado en los documentos sigue vigente, entender exactamente cómo se envía la posición/telemetría, y construir un modelo de consumo (batería + datos) por fase de actividad antes de decidir el modelo de suscripción del Bloque de Negocio.

---

## 1) ¿Cómo se envía exactamente la posición/telemetría?

Fuente: `ARES_Firmware_Comms_Conectividad_v1.md` (documento técnico vigente para firmware/backend).

- **Protocolo primario:** MQTT (hacia broker EMQX) — `devices/{device_id}/telemetry` (PUB del dispositivo).
- **Fallback:** HTTP `POST /api/v1/ingest` — usado si MQTT falla, o para el envío en batch tras un periodo de store & forward.
- **Estructura del payload:** no es "un punto GPS por mensaje". Cada envío es un **batch** que agrupa:
  - Un `gnss_fix` (lat/lon/accuracy/satélites/velocidad) — puede ser nulo si no hay fix.
  - Un `activity_batch`: array con un objeto **por minuto** de actividad (pasos, cadencia, intensidad, segundos en cada estado, eventos como "sprint_start").
  - Bloques de `power` (batería/temperatura), `comms` (rssi, tipo de red) e `integrity` (versión de firmware).
- **Frecuencia de envío por modo** (de `02_ESPECIFICACION_TECNICA.md` §4.1.1 y `ARES_Firmware_Comms_Conectividad_v1.md` §5, ambos ya coherentes entre sí):

| Modo | Frecuencia de fix GNSS | Qué se envía |
|---|---|---|
| **REST** | GNSS casi siempre OFF | Heartbeat de batería/estado cada 10–30 min |
| **WALK** | Fix cada 30–60s | Batch de actividad acumulada + fix GNSS |
| **RUN** | Fix cada 5–10s | Batch de actividad acumulada + fix GNSS |
| **LIVE** (forzado por usuario) | Fix cada 2–3s | Payload mínimo (solo GNSS), timeout máx. 10-15 min |
| **LOST** (forzado por usuario) | Ráfagas de 2–3s por evento de riesgo | Igual que LIVE, activado por proximidad a geofence o aceleración alta |

- **Por qué importa para el coste:** el diseño ya está optimizado para minimizar transmisiones (que son lo que más batería y datos consume por el overhead de conexión LTE), agrupando datos en vez de enviar cada punto individualmente. Esto es coherente con el objetivo de negocio de mantener el coste de datos bajo.

## 2) ¿Puede la actualización OTA de firmware hacerse por WiFi doméstico en vez de por la SIM celular?

**Sí, y ya es el diseño vigente, no solo una mención de paso.** Confirmado en dos documentos:
- `ARES_Documento_SIM_eSIM_v1.0.md` §3.1: "WiFi ↔ para actualizaciones de firmware (OTA)".
- `ARES_Firmware_Comms_Conectividad_v1.md` §3.2.3: "WiFi AP temporal: setup/OTA preferente en casa (`Roco_Setup_123` / 'WiFi conocida')".
- `02_ESPECIFICACION_TECNICA.md` §2.4: "WiFi → Detección de zonas seguras (ahorro de energía) y actualizaciones OTA".

**Implicación práctica:** el firmware debe **preferir WiFi para OTA siempre que el dispositivo detecte una red conocida** (la misma lógica que ya usa para "zona segura"/ahorro de batería), y solo caer a descarga OTA por celular como fallback si no hay WiFi disponible tras N días sin actualizar. Esto es coherente con el objetivo de mantener el consumo de datos de pago bajo — las actualizaciones de firmware pueden ser de varios cientos de KB a unos pocos MB, y forzarlas siempre por WiFi evita que compitan con el presupuesto de datos de telemetría. **Esto debe quedar como requisito explícito** (no estaba en la lista de "Requisitos mínimos para Ready for Field Test" de `ARES_Firmware_Comms_Conectividad_v1.md` §11 — se añade aquí como gap a cerrar).

## 3) ¿Qué pasa cuando se agota el plan de datos de 1NCE?

**Verificado en vivo (julio 2026) contra la documentación pública de 1NCE** — ver fuentes al final:

- El plan referenciado en los documentos de ARES es **1NCE "High Data IoT"** (5€/GB + 12€ alta única), **no** el plan estándar "Lifetime Flat" (500MB/10 años). Esto es importante porque ambos planes se comportan de forma muy distinta al agotar datos:
  - **High Data IoT (el que usa ARES):** es pago por uso puro, **sin cuota fija mensual, sin compromiso de volumen y sin penalización por exceso**. No hay "agotar el plan" en el sentido de corte de servicio — simplemente se sigue pagando 5€ por cada GB adicional consumido. El "250MB/mes" que aparece en los documentos de ARES es una **cifra de referencia de consumo esperado**, no un tope contratado.
  - **Lifetime Flat (NO es el plan de ARES, solo para contraste):** al agotar los 500MB incluidos, la SIM sigue activa 18 meses más, permitiendo comprar otro bloque de 500MB por 12€; si no se recarga en ese plazo, la SIM se desactiva automáticamente. Mencionado aquí solo para dejar constancia de que ARES **no** está en este modelo.
- **Conclusión:** con el plan High Data, no hay riesgo de "corte de servicio por datos agotados" — el riesgo real es puramente económico (pagar más si el consumo real supera la estimación de 250MB/mes). Esto refuerza la necesidad del modelo de consumo del punto 4 para saber si esa estimación es realista.

## 3.1) Cláusulas contractuales reales de 1NCE (verificado en el PDF legal, no solo en la web de marketing)

**Corrección importante respecto a la primera versión de este documento:** el análisis inicial se basó en la web pública de 1NCE ("sin compromiso de volumen, sin cuota fija"), que es cierto pero **no es lo mismo que "sin permanencia contractual"**. Se ha descargado y leído el contrato real (`1NCE GmbH — General Terms and Conditions Part A`, v01_26, y `Service-Specific Terms for 1NCE High Data IoT`, v01_26) y esto es lo que dice de verdad:

- **Permanencia mínima: 12 meses por SIM** (§4 de los términos específicos de High Data IoT). Cada SIM activada es un contrato independiente. Si no se cancela con **2 meses de preaviso** antes de que acabe ese año, **se renueva automáticamente por otro año** (§6.1.b Part A).
- **Subida de precios permitida, pero con condiciones** (§5.8 Part A):
  - Solo si hay un aumento real y demostrable de los costes de 1NCE (red mayorista, personal, energía, impuestos) — no es una subida discrecional libre.
  - **No puede subir precios hasta que el contrato lleve al menos 12 meses activo.**
  - Como máximo **una subida por año contractual** a partir de ahí.
  - **Aviso por escrito con al menos 1 mes de antelación** antes de que la subida sea efectiva.
- **Excepción de IVA (§5.9):** si cambia el IVA legal, 1NCE ajusta el precio automáticamente y el cliente **no tiene derecho a cancelar por ese motivo concreto**.
- **Suspensión del servicio** (§1.5 del anexo específico): 1NCE puede suspender una SIM si no hay actividad de datos/SMS durante 18 meses continuos, si hay impago, o si se usa fuera de los países/región acordados en el "Forecast" de despliegue.

**Implicación práctica para ARES:** el modelo de negocio debe asumir que el precio de datos (5€/GB) está protegido contractualmente durante el primer año, y que cualquier subida posterior será progresiva (máx. 1 vez/año, con 1 mes de aviso) y justificada por coste real — no un riesgo de "nos suben el precio de golpe x5 sin aviso". El riesgo real de negocio no es una subida repentina, sino la **permanencia de 12 meses con renovación automática**: hay que llevar un calendario de cancelación por lote de SIMs si en algún momento se quiere migrar de proveedor, porque no se puede salir de un día para otro sin ese preaviso de 2 meses.

**Fuentes (PDF legal, descargado y verificado línea por línea):**
- `1NCE GmbH — General Terms and Conditions, Part A` (v01_26): https://a.storyblok.com/f/335000/x/5110e3e0f5/1nce-gmbh-part-a-gtc-01_2026-en.pdf
- `Service-Specific Terms for 1NCE High Data IoT` (v01_26): https://a.storyblok.com/f/335000/x/729239b556/1nce-high-data-iot-service-specific-terms-gtcs-01_2026.pdf

## 4) ¿Sigue siendo 1NCE la mejor opción frente a Simbase?

Del propio `ARES_Documento_SIM_eSIM_v1.0.md` (ya documentado, no requiere cambio):
- **1NCE High Data:** ≈1,25€/mes a 250MB, sin cuota fija, cobertura en 170+ países — mejor para el SKU Global.
- **Simbase (España/UE):** ≈1,55€/mes a 250MB (incluye una cuota diaria de 0,01€/SIM activa) — mejor encaje si el dispositivo nunca sale de España/UE, pero ligeramente más caro que 1NCE a este volumen por la cuota diaria fija.
- **Recomendación (sin cambios sobre lo ya documentado):** mantener la estrategia de 2 SKU ya propuesta — 1NCE para el SKU Global, Simbase como alternativa a evaluar solo si en algún momento se lanza un SKU "España/UE únicamente" donde el coste diario fijo de Simbase deje de ser relevante (por ejemplo, si se negocia un descuento por volumen que no aplica a 1NCE en ese tramo).

**Verificación en vivo confirma que 1NCE High Data sigue activo con las mismas condiciones** (5€/GB, 12€ alta, sin cuota fija, 170+ países, velocidades hasta 25 Mb/s) — no hace falta cambiar de proveedor.

---

## 5) Modelo de consumo (batería + datos) por fase de actividad

**Objetivo:** cuantificar, no asumir, el consumo real de cada estado, para (a) validar si 250MB/mes es realista, y (b) dar una base numérica a la futura estimación de FC/esfuerzo por IMU (Bloque C), que añadirá un pequeño coste extra de muestreo.

### 5.1 Supuestos de partida — ACTUALIZADO con datasheets reales de fabricante

**Corrección importante respecto a la primera versión de este análisis:** la primera pasada usaba cifras genéricas "de referencia de la industria" (ej. "~5 mAh por fix GPS"), que resultaron estar mal calibradas y generaban una discrepancia grave con la especificación oficial (~140mAh/día). Se ha vuelto a calcular todo con **datasheets reales de los componentes específicos de ARES**:

- **SIMCom SIM7000G** (User Manual, tabla de consumo VBAT=3.8V): GNSS tracking activo = **34 mA** (fijo mientras está encendido, no "por fix"); GNSS sleep = 1 mA; LTE-M idle (registrado, sin transmitir) = **11 mA**; LTE-M TX @10dBm (potencia media/realista) = **116 mA**; LTE-M TX @23dBm (peor caso, celda lejana/mala cobertura) = **160 mA**.
- **ESP32-S3** (datasheet Espressif + medición de módulo WROOM-1 real): deep sleep = **~8 µA**; modem sleep (CPU activa, radio baja) = ~15 mA; activo procesando = **~24 mA**; pico WiFi TX = ~310 mA (no aplica en uso normal, solo si se usa WiFi para OTA/zona segura).
- Tamaño de payload de telemetría: se mantiene la estimación de **250 bytes/envío en JSON** (pendiente de medición real, ver §9) — esto no cambia con los datasheets, es un dato de diseño de software, no de hardware.

Fuentes: SIM7000G User Manual (SIMCom, tabla de current consumption pág. 48) y ESP-IDF Programming Guide / datasheet ESP32-S3 (Espressif).

### 5.2 Tabla de consumo recalculada por fase (1 hora continua en ese modo, cifras de datasheet real)

| Fase | Consumo batería (mAh/hora) | Cómo se compone |
|---|---|---|
| **REST** | **~1,2 mAh/hora** | ESP32 en deep sleep (8µA) + LTE en bajo consumo casi todo el tiempo, con ~3 heartbeats/hora de ~2s de TX cada uno |
| **WALK** | **~71,6 mAh/hora** | GNSS tracking continuo (34mA) + ESP32 activo (24mA) + LTE con TX breve en cada envío (~90 envíos/hora) |
| **RUN** | **~84,8 mAh/hora** | Igual que WALK pero con más envíos/hora (~540) por la mayor frecuencia de fix |
| **LIVE** (ventana de 12 min, timeout real) | **~25,7 mAh en esa ventana** (no por hora — el timeout de 10-15 min lo impide) | GNSS tracking + TX cada 2-3s a máxima potencia (peor caso 23dBm) durante la ventana completa |

**Diferencia clave frente al primer cálculo (genérico):** antes asumía que cada fix GNSS individual costaba varios mAh de forma aislada; en la práctica, el GNSS consume una corriente **fija mientras está activo** (34mA constantes durante todo el tiempo que se mantiene encendido para no perder el fix), independientemente de cada cuánto se envíe el dato. Esto hace que el coste real de WALK/RUN sea mucho menor de lo que había calculado la primera vez.

### 5.3 Patrón de uso típico y escenarios — recalculados

| Escenario | Consumo/día | Autonomía Medium (2750mAh) | Autonomía Large (4000mAh) |
|---|---|---|---|
| **Típico** (8h REST + 2h WALK) | ~153 mAh | **~18 días** | **~26 días** |
| **Muy activo** (6h REST + 1,5h WALK + 1h RUN) | ~200 mAh | ~13,8 días | ~20 días |
| **Caso extremo del usuario: 10h actividad/día** (5h WALK + 5h RUN) + 14h REST | ~799 mAh | **~3,4 días (~82,6 horas)** | **~5 días (~120 horas)** |
| Extremo puro: 10h RUN continuo + 14h REST | ~865 mAh | ~76,3 horas (~3,2 días) | ~111 horas (~4,6 días) |

**Conclusión: con datasheets reales, el "~20 días" de la especificación oficial (`02_ESPECIFICACION_TECNICA.md` §5.1) es coherente y defendible** — el escenario típico da ~18 días en Medium, muy cerca de esa cifra. **La discrepancia detectada en la primera versión de este análisis era un error de calibración de mi modelo (cifras genéricas de industria mal ajustadas), no un problema del documento técnico de ARES.** Dicho esto, estas cifras siguen siendo estimaciones basadas en datasheet de fabricante en condiciones de laboratorio (VBAT=3.8V, condiciones ideales) — **la medición de banco real con el hardware integrado final sigue siendo necesaria** para confirmar que el diseño de PCB/antena/carcasa no añade pérdidas adicionales no capturadas por el datasheet del chip aislado.

### 5.4 Encaje con el plan de datos de 1NCE

**Escenario típico:** en el patrón usado en `02_ESPECIFICACION_TECNICA.md` §5.1 (8h REST + 2h WALK + resto reposo/valla), el consumo de datos estimado es: 8 KB (REST) + 2×20 KB (WALK, valor medio) = ~48 KB/día → **~1.4 MB/mes**.

**Escenario de actividad máxima realista (perro de nivel "Alta" actividad, ver `knowledge_base` §B.1: 90-150 min de ejercicio vigoroso/día):** 6h REST + 1.5h WALK + 1h RUN → **~700 envíos/día, ~171 KB/día → ~5 MB/mes**. Sigue estando muy por debajo del límite de referencia.

**Peor caso extremo (mismo perro muy activo + 1h acumulada de modo LIVE/LOST en el día, repartida en varias activaciones de búsqueda/seguimiento en vivo — un uso ya considerablemente por encima de lo habitual):** **~2.200 envíos/día, ~537 KB/día → ~15.7 MB/mes**.

**Conclusión sobre el "techo" de consumo de datos:** incluso llevando el patrón de uso a un extremo poco realista (máxima actividad física + uso frecuente de modo Live/Lost), el consumo proyectado (~15.7 MB/mes) sigue siendo **~6% de la referencia de 250MB/mes**. Esto está **muy por debajo** de los 250MB/mes de referencia — hay margen amplísimo, incluso si las cifras de payload están subestimadas por un factor de 10x.

**CORRECCIÓN IMPORTANTE (releída con más cuidado el contrato de 1NCE, §3.3 de los términos específicos de High Data IoT):** la facturación de 1NCE **no es fraccionaria/prorrateada por MB individual** — se factura por **GB completo redondeado hacia arriba**, y además **sobre el consumo AGREGADO de todas las SIMs del cliente juntas**, no SIM por SIM. Esto significa:
- A **bajo volumen** (fase prototipo/preventa, 5-100 dispositivos): el consumo agregado de todos los dispositivos típicos apenas llega a unos pocos MB/mes en total, por lo que 1NCE factura el **mínimo de 1 GB (5€/mes en total, para toda la flota)** — repartido entre pocos dispositivos, el coste por unidad es bajo pero no estrictamente proporcional al consumo real (ej. con 5 dispositivos típicos, sale a ~1€/mes/dispositivo; con 100 dispositivos típicos, baja a ~0,05€/mes/dispositivo).
- A **escala real** (1.000+ dispositivos, la fase de negocio que importa para el pricing definitivo): el consumo agregado ya supera 1GB con margen, y el coste por dispositivo converge a las cifras que ya se habían calculado — del orden de 0,01-0,03€/mes/dispositivo en uso típico, hasta ~0,77€/mes/dispositivo en el escenario extremo x10 (con 1.000 dispositivos, ese escenario agregado da ~154 GB/mes = 770€/mes total repartido entre 1.000 unidades).
- **Conclusión:** el análisis de margen del Plan Esencial a 5€/mes (§8) sigue siendo válido y conservador a escala real — el efecto de redondeo por GB agregado no cambia la conclusión de fondo (datos nunca son el cuello de botella), pero es importante que quien gestione la facturación con 1NCE entienda que se paga por **GB agregados de toda la flota**, no por dispositivo individual — la factura de 1NCE será una sola cifra mensual a repartir internamente entre los dispositivos activos, no 1.000 facturas individuales.
- **Los datos nunca son el cuello de botella** — el plan de 1NCE (High Data, sin cuota fija, pago por GB) tiene margen amplísimo en todos los escenarios. La batería, aunque recalculada con datasheets reales y ahora coherente con la especificación oficial (~18-20 días en uso típico), sigue siendo el recurso más sensible al patrón de uso real del perro (ver §5.3: de ~18 días en uso típico a ~3-5 días si el perro hace 10h de actividad intensa al día) — cualquier lectura adicional de sensores en REST (ej. la estimación de FC del Bloque C) debe seguir validándose contra este presupuesto antes de activarse por defecto.
- **Recomendación:** el modelo de negocio (Bloque B) puede tratar el coste de datos como prácticamente fijo y bajo (~1,25-2€/mes por dispositivo con margen de sobra). La autonomía ya tiene un modelo defendible con datasheets de fabricante, pero la medición de banco con el hardware integrado final sigue siendo el paso que falta antes de comprometer cifras definitivas en marketing.

---

## 6) Presupuesto energético del sistema de LEDs

**Objetivo del usuario:** confirmar si ~2 horas de uso intensivo de LED consumen razonablemente ≤20% de batería en el peor caso. No es un bloqueante duro (el usuario acepta recargar si hace falta), pero debe quedar cuantificado.

### 6.1 Lo que ya existe en el diseño para ahorrar energía (confirmado en código)
El firmware (`firmware/src/led_controller.h`) ya implementa varias medidas de ahorro, no es un diseño "siempre encendido":
- **Alimentación directa desde VBAT sin booster de 5V** (menos pérdida de conversión que un diseño con step-up).
- **3 canales PWM (R/G/B)**, cada uno controla en paralelo los LEDs de su color en las 2 zonas "L" (2 LEDs por color y zona → 4 LEDs por canal).
- **Ningún modo mantiene los 3 canales al 100% de forma continua:** `LED_VISIBILITY` parpadea a 0.5Hz con 50% de duty cycle; `LED_FIND` hace estrobo a 4Hz con 50% duty cycle y usa solo 2 canales (cian = verde+azul, sin rojo); los modos de estado (`LED_STATUS_OK/WARNING/ERROR`) usan un único canal de color con un patrón de "respiración" (rampa 0→100%→0 en 2s), cuyo brillo medio es ~50% del pico.
- **Bloqueo por batería baja:** `canUseLeds()` ya impide el uso manual de LEDs por debajo del 15% de batería (`BATTERY_LED_BLOCK_PCT`), dejando solo destellos informativos mínimos.

### 6.2 Cálculo (estimación de diseño, sin medición de banco todavía)
No hay corriente por LED especificada en los documentos de hardware — se usa aquí el valor típico de datasheet para un LED SMD 1206 de alta intensidad limitado por resistencia serie (**~20mA por LED a brillo máximo**), como cifra de referencia conservadora hasta que exista medición real.

| Modo LED | Canales activos | Duty cycle efectivo | Corriente media estimada | Consumo en 2h | % batería Medium (2750mAh) |
|---|---|---|---|---|---|
| **LED_VISIBILITY** (blanco, paseo nocturno) | 3 (R+G+B) | 50% (parpadeo 1s on/1s off) | ~120 mA | ~240 mAh | **~8.7%** |
| **LED_FIND** (cian, modo búsqueda) | 2 (G+B) | 50% (estrobo 4Hz) | ~80 mA | ~160 mAh | **~5.8%** |
| **LED_STATUS pulse** (un color, respiración) | 1 | ~50% (rampa triangular) | ~40 mA | ~80 mAh | **~2.9%** |

### 6.3 Conclusión
Incluso en el **peor caso realista** (2h continuas de `LED_VISIBILITY` en blanco, el modo que más canales y más duty cycle usa), el consumo estimado es **~8.7% de la batería Medium — muy por debajo del objetivo de ≤20%** fijado por el usuario. El diseño actual (parpadeo/estrobo/respiración, nunca 3 canales al 100% fijo) ya incorpora suficiente ahorro por sí mismo; no se identifica ningún cambio de diseño necesario en este momento. Queda pendiente, igual que el resto de cifras de este documento, **confirmar con medición de banco real** el consumo por LED (mA a la resistencia serie definida en el diseño final) para sustituir el valor de datasheet genérico usado aquí.

---

## 8) Pricing del Plan Esencial — decisión cerrada (5€/mes)

**Decisión del usuario:** Plan Esencial fijado en **5€/mes** (por encima del mínimo viable calculado de 2,99€), sin subir el precio del hardware, para tener colchón de margen amplio.

| Escenario de consumo | Coste real de datos/mes | Margen bruto a 5€/mes | Margen neto (tras 35% carga fiscal) | Margen neto/año/cliente |
|---|---|---|---|---|
| Típico | ~0,01€ | 4,99€ | 3,24€ | 38,92€ |
| Muy activo | ~0,02€ | 4,98€ | 3,24€ | 38,84€ |
| **Extremo x10 (referencia de diseño)** | **~0,77€** | **4,23€** | **2,75€** | **32,99€** |
| Saturación x100 (casi imposible, colchón) | ~7,68€ | -2,68€ | -1,74€ | -20,90€ |

A 5€/mes, el margen se mantiene amplio y positivo hasta el escenario x10 (el techo de consumo realista ya modelado en §5.4). Solo el escenario x100 (saturación por uso de modo Live casi permanente, que el propio timeout de 10-15 min hace estructuralmente improbable) generaría pérdida, y sería puntual y residual, no un patrón de negocio.

## 9) Pendiente de cierre (no asumir, medir)
1. **Medición de banco real** de mAh/hora en REST, WALK y RUN con el hardware v4.0 definitivo — para sustituir las cifras de referencia de la industria usadas en este documento por datos propios.
2. **Medición real de tamaño de payload** en bytes tal como lo serializa el firmware (JSON vs CBOR/Protobuf) — para afinar la proyección de MB/mes.
3. Añadir el requisito de "OTA preferente por WiFi, fallback celular" a la checklist de "Ready for Field Test" en `ARES_Firmware_Comms_Conectividad_v1.md` §11.
4. **Medir corriente real por LED** (mA a la resistencia serie del diseño final) para confirmar el cálculo del §6 con datos propios en vez del valor de datasheet genérico usado aquí.
5. Una vez exista el hardware físico, repetir este análisis con datos reales antes de publicar cualquier cifra de autonomía en marketing.

## Fuentes verificadas en vivo (julio 2026)
- 1NCE High Data IoT — pricing y condiciones: https://www.1nce.com/en-eu/1nce-connect/features/high-data-iot
- 1NCE Data Services (comportamiento del plan Lifetime Flat al agotar volumen, usado aquí solo de contraste): https://help.1nce.com/dev-hub/docs/data-services-features-limitations
