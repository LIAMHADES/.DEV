# ARES v4.0 — Risk Register (RR-XXX)
**Versión:** 1.0 | **Origen:** sesión de cierre de brechas de producto, negocio y diferenciación (ver `01_PRODUCTO_Y_NEGOCIO.md` §3.11 para el Decision Log asociado).

Formato por riesgo: descripción, probabilidad, impacto, dueño, mitigación, test de validación — según el protocolo exigido para el proyecto ARES.

---

## RR-001: El firmware es una cáscara simulada, no una integración real — EN PROGRESO (driver escrito contra datasheet, sin validar)
- **Descripción:** `imu_manager.h` generaba datos falsos (`random()`) en vez de leer el hardware real. El diferenciador central "IMU+GNSS fusion" no existía en código, solo en documentos.
- **Confirmado con el usuario:** no hay hardware físico disponible todavía (ni placa de desarrollo genérica ni componentes sueltos) — el proyecto sigue 100% en fase de diseño/documentación. Por eso RR-001 no se puede cerrar con pruebas reales en esta sesión.
- **Trabajo realizado en esta sesión:** se reescribió `firmware/src/imu_manager.h` con un driver I2C real basado en el **BMI270 Datasheet oficial de Bosch** (rev. 06) — secuencia de inicialización, mapa de registros (CHIP_ID, PWR_CTRL, PWR_CONF, ACC_CONF, GYR_CONF, burst read de datos), y lectura real de acelerómetro/giroscopio vía `Wire.h`. Cada bloque de código incluye comentarios señalando qué está verificado contra datasheet y qué sigue pendiente.
- **Lo que SIGUE faltando y no se puede resolver sin hardware o sin más trabajo:**
  1. **El "config file" binario de Bosch (~8KB) no está vendorizado.** El BMI270 exige cargar este blob de configuración antes de funcionar — no es opcional. Hay que copiarlo tal cual desde el repo oficial (`BMI270-Sensor-API/bmi270.c` en GitHub de Bosch Sensortec), no reescribirlo a mano. Sin esto, el sensor no producirá datos válidos aunque el resto del driver esté bien.
  2. **Dirección I2C asumida (0x68), no confirmada** contra el esquemático final — depende del strapping del pin SDO, que no está especificado en los documentos de hardware de ARES.
  3. **Pines SDA/SCL no confirmados** en `config.h` (no estaban definidos, a diferencia de los pines de LED que sí lo están).
  4. **Escalado de LSB a unidades físicas (g, dps) no implementado** — depende del rango configurado (ACC_RANGE/GYR_RANGE), que tampoco está fijado en la documentación de ARES todavía.
  5. **Umbrales de clasificación de actividad (REST/WALK/JOG/RUN) sin calibrar** — los literales heredados del código anterior (120, 80, `MOTION_THRESHOLD_MG`) estaban ajustados para valores simulados aleatorios, no para LSB reales del sensor.
  6. **Step count real no implementado** — requiere el step-counter integrado del BMI270 (feature del config file de Bosch), no la heurística actual.
- **Probabilidad:** Alta (confirmado, no es hipotético).
- **Impacto:** Crítico — toda la propuesta de valor de salud/actividad (y la estimación de FC/esfuerzo, RR-002) depende de que esta integración exista de verdad.
- **Dueño:** Firmware/embebido.
- **Mitigación:** en cuanto haya hardware físico disponible: (1) vendorizar el config file oficial de Bosch, (2) confirmar SDO/SDA/SCL contra el esquemático, (3) correr la secuencia de inicialización y confirmar `INTERNAL_STATUS` bit 0, (4) calibrar umbrales de actividad con movimiento real conocido.
- **Test de validación:** banco de pruebas con el chip real, comparar step count / clasificación de actividad contra un patrón de movimiento conocido (ej. caminar N pasos contados a mano).

## RR-002: Estimación de FC/esfuerzo vía IMU — precisión no validada
- **Descripción:** la estimación de frecuencia respiratoria/esfuerzo en reposo (`SPEC_04_INTELLIGENCE_HEALTH.md` §1.4) es un método indirecto (micro-movimiento vía acelerómetro), no una medición directa. Puede tener precisión limitada o ruido significativo, especialmente en perros pequeños o con pelaje denso que amortigua el micro-movimiento detectable.
- **Probabilidad:** Media-Alta — es un método ya usado por Tractive, pero ARES no tiene validación propia todavía.
- **Impacto:** Medio — si se comunica mal (como medición exacta en vez de estimación), genera desconfianza si el usuario la contrasta con un veterinario. Si se comunica bien ("estimación", con baseline individual), el riesgo se limita a utilidad limitada, no a credibilidad de marca.
- **Dueño:** Firmware (algoritmo) + Producto (comunicación).
- **Mitigación:** (1) nunca presentar como medición clínica; (2) validar con datos reales antes de publicitar cualquier cifra de precisión; (3) usar baseline individual (comparar contra el propio historial del perro) en vez de valores absolutos, que es más robusto a errores sistemáticos de calibración.
- **Test de validación:** comparar la estimación contra observación manual (conteo de respiraciones/minuto por el dueño) en una muestra de perros de distintos tamaños/pelajes antes de lanzar la función.

## RR-003: Coste en batería del muestreo de IMU más fino durante REST — no medido
- **Descripción:** la estimación de FC/esfuerzo (RR-002) requiere un muestreo de IMU más frecuente/sensible durante REST que el actual (que solo confirma "sin locomoción" a baja frecuencia). El impacto real en consumo no está medido en banco.
- **Probabilidad:** Media — es plausible que sea pequeño (no requiere GNSS ni módem activo), pero no está confirmado.
- **Impacto:** Medio — si el coste es mayor de lo esperado, podría erosionar la autonomía en REST, que hoy es el estado de menor consumo y el que más horas acumula al día (8h+ típicas).
- **Dueño:** Firmware/Hardware.
- **Mitigación:** medir en banco el consumo de IMU en modo "REST + muestreo fino" vs "REST estándar" antes de activar esta función por defecto; considerar hacerlo opcional/activable por el usuario si el coste es significativo.
- **Test de validación:** medición de corriente (mA) en banco con el hardware definitivo, comparando ambos modos de muestreo durante 1h de reposo real.

## RR-004: Sensor PPG dedicado — descartado por ahora, no eliminado del radar
- **Descripción:** se evaluó un sensor óptico dedicado (PPG, tipo MAX30102/MAX86141) para medición directa de pulso/SpO2 — el enfoque de Invoxia. El usuario decidió **no implementarlo ahora**: "muy difícil de implementar y ahora mismo no es necesario".
- **Motivo del descarte (documentado para no perder el análisis si se retoma):**
  - Reto de diseño industrial genuino: contacto óptico contra piel a través del pelaje (a diferencia de wearables humanos de muñeca) requiere sonda/paleta con mecanismo de presión y geometría de separación de pelo.
  - Los LEDs de PPG son de alto consumo — conflicto directo con la filosofía "IMU-first, ultra bajo consumo" de v4.0.
  - Requiere fusión IMU+PPG para compensar artefactos de movimiento (trabajo de firmware no trivial).
  - Nueva tabla en BD (`VitalsReading` o similar, cadencia de muestreo distinta a `Location`).
  - Bandera regulatoria: cualquier claim de "salud/vital" invita a más escrutinio (framing cuasi-médico).
- **Probabilidad de que se retome:** a evaluar en una fase futura, si la estimación por IMU (RR-002) resulta insuficiente para diferenciarse o si el negocio (una vez cerrado el Bloque de prioridad 2) justifica la inversión en un sensor dedicado como feature premium.
- **Impacto de mantenerlo descartado:** bajo a corto plazo (ningún competidor analizado lo tiene tampoco, salvo Invoxia con approach distinto) — es oportunidad de diferenciación futura, no una carencia urgente.
- **Dueño:** Producto (decisión de roadmap).
- **Mitigación:** ninguna acción requerida ahora; mantener este RR como registro para no repetir el análisis desde cero si se retoma.
- **Test de validación:** N/A hasta que se decida retomar.

## RR-005: Discrepancia entre consumo diario estimado (~140 mAh/día) y el modelo de consumo por fase — RESUELTO (era error de calibración propio, no del documento)
- **Descripción original:** el primer modelo de consumo por fase de actividad, usando cifras genéricas de referencia de la industria (no del chip específico de ARES), sugería que 2h de paseo activo (WALK) podrían consumir hasta ~1000 mAh — muy por encima de lo que permitiría la cifra de "~140 mAh/día" ya publicada en `02_ESPECIFICACION_TECNICA.md` §5.1.
- **Resolución:** se recalculó el modelo completo con **datasheets reales** del SIMCom SIM7000G (GNSS tracking = 34mA fijos mientras está activo, no "por fix") y del ESP32-S3 (Espressif). Con estas cifras de fabricante, el escenario típico da **~153 mAh/día (~18 días en Medium)** — coherente y muy cercano al "~20 días" oficial. **La discrepancia era un error de calibración de mi primer modelo (sobrestimaba el coste por fix GNSS), no un problema real de la especificación técnica de ARES.**
- **Bonus — respuesta al caso extremo del usuario (10h de actividad/día):** con las cifras reales, ese escenario da **~799 mAh/día → ~3,4 días de autonomía en Medium, ~5 días en Large** — mucho más razonable que las 2-6 horas que arrojaba el primer cálculo erróneo. Ver `ARES_Analisis_Red_y_Consumo_v1.md` §5.3 para la tabla completa.
- **Riesgo residual (por qué no se cierra del todo):** estas cifras siguen siendo de datasheet de fabricante en condiciones de laboratorio (chip aislado, VBAT=3.8V) — el diseño de PCB, antena, y carcasa final de ARES puede introducir pérdidas adicionales no capturadas por el datasheet del componente aislado. Sigue sin poder cerrarse del todo sin hardware físico (confirmado: el usuario no tiene hardware disponible todavía).
- **Probabilidad de que la medición real difiera algo de este recálculo:** Media — es normal que la integración real (antena, layout de PCB, pérdidas de conector) añada un 10-30% de consumo extra sobre el datasheet del chip aislado, pero ya no se espera una discrepancia de orden de magnitud como la que sugería el primer cálculo.
- **Impacto:** Medio (bajó de Alto) — con el modelo recalculado, el riesgo de prometer autonomía muy alejada de la realidad se reduce sustancialmente, aunque sigue sin ser una medición confirmada.
- **Dueño:** Hardware/Firmware.
- **Mitigación:** usar las cifras recalculadas (§5.3 del análisis de red) como base de comunicación provisional ("hasta ~18-20 días en uso típico, según patrón de actividad"), pero seguir marcando como "estimación de diseño" hasta medición de banco con el hardware integrado final.
- **Test de validación:** medición de mAh/hora real en REST, WALK y RUN con el prototipo físico integrado (PCB + antena + carcasa final), comparando contra las cifras de datasheet aislado de este documento para cuantificar la pérdida real de integración.

## RR-006: Claim de precisión GNSS "<1m" sin validación de campo
- **Descripción:** ya documentado y corregido en los textos (ahora "objetivo <1m, pendiente de validación de campo"), pero el riesgo de fondo persiste: no hay datos de TTFF/p50/p90/p95 que respalden la cifra.
- **Probabilidad:** Media — el hardware (Ignion A101+LNA) es una elección razonable, pero la precisión real depende de integración, antena, carcasa y entorno de uso (bosque/urbano).
- **Impacto:** Alto si se compromete "<1m" en marketing antes de validar — mismo patrón de riesgo que RR-005.
- **Dueño:** Hardware/RF.
- **Mitigación:** plan de test de campo (ya mencionado como pendiente en `SPEC_02_TRACKING_CORE.md` y en el propio `02_ESPECIFICACION_TECNICA.md`) antes de publicar la cifra como claim comercial definitivo.
- **Test de validación:** mediciones de precisión en escenarios reales (urbano, bosque, cielo abierto) con el hardware final, calculando percentiles p50/p90/p95 de error de posición.

## RR-007: Modelo de negocio "Plan Esencial" — CERRADO (5€/mes)
- **Descripción:** existían dos opciones viables (suscripción mínima visible vs. conectividad pre-pagada en el hardware) para el tier de entrada. **Decisión tomada:** suscripción de 5€/mes, sin subir el precio del hardware (DL-008 en `01_PRODUCTO_Y_NEGOCIO.md` §3.11).
- **Estado:** Cerrado — margen verificado positivo en todos los escenarios de consumo salvo el x100 (saturación casi imposible por el timeout de LIVE). Ver `ARES_Analisis_Red_y_Consumo_v1.md` §8 para la tabla completa.
- **Riesgo residual identificado durante el cierre — cláusulas contractuales de 1NCE:** verificado el contrato legal real (no solo la web de marketing): permanencia de 12 meses por SIM con renovación automática si no se cancela con 2 meses de preaviso; subida de precio permitida solo tras 12 meses de contrato, máx. 1 vez/año, con 1 mes de aviso, y solo si hay coste real incrementado de 1NCE (no es discrecional libre). Riesgo bajo-medio, gestionable con calendario de cancelación por lotes de SIM si se decide cambiar de proveedor.
- **Dueño:** Negocio/Producto.
- **Mitigación:** mantener Simbase cualificado como proveedor secundario (ya evaluado) por si se necesita migrar; llevar calendario de fechas de renovación por lote de SIMs activadas.
- **Test de validación:** N/A — cerrado como decisión de negocio.

## RR-008: Coste de la celda LiPo (123450, 2750mAh) sin cotización directa verificada
- **Descripción:** se investigaron precios de mercado de celdas LiPo por volumen para evaluar si el coste asumido en `Hardwear.txt` (~6,5€ Medium / ~9,5€ Large) tiene margen de ahorro. Se confirmaron precios de mercado genéricos (4000mAh a ~4,4-4,8€/unidad a 1000+ uds) que sugieren que la cifra actual de ARES **no está sobrevalorada** — pero no se pudo obtener una cotización específica para el formato exacto 123450/2750mAh de ARES, ya que los fabricantes (LiPol Battery, Benzo Energy/UFine, DNK Power) solo publican precio bajo petición directa.
- **Probabilidad:** Baja de que haya un ahorro grande aquí — la batería no parece ser el componente sobrevalorado del BOM.
- **Impacto:** Bajo — incluso si hay 1-2€/unidad de ahorro potencial, es marginal comparado con el módulo LilyGo (28€, 49% del coste base).
- **Dueño:** Compras/Hardware.
- **Mitigación:** pedir cotización directa a 2-3 fabricantes (LiPol Battery, Benzo Energy/UFine, DNK Power) especificando 123450, 2750mAh, 1S, a MOQ de 1000 y 5000 unidades — acción comercial, no técnica ni de búsqueda web.
- **Test de validación:** comparar cotizaciones reales recibidas contra la cifra actual de `Hardwear.txt` una vez lleguen.

## RR-009: Módulo LilyGo T-SIM7000G S3 — mayor palanca de ahorro de hardware, no explorada en esta sesión
- **Descripción:** el módulo integrado LilyGo representa el 49% del coste base del hardware (28€ de 57,4€). Sustituirlo por chips sueltos (SIM7000G + ESP32-S3) en un PCB propio tiene potencial de ahorro significativo, pero requiere I+D de diseño de PCB, validación RF propia y recertificación — el usuario decidió explícitamente no investigar esto en esta sesión y dejarlo en el radar.
- **Probabilidad:** N/A — decisión de alcance, no un riesgo técnico en sí.
- **Impacto:** Alto potencial de ahorro a largo plazo (posible reducción significativa del coste unitario a partir de cierto volumen), pero con coste de I+D inicial que solo se amortiza a escala.
- **Dueño:** Hardware/Producto.
- **Mitigación:** ninguna acción requerida ahora; revisitar cuando el proyecto entre en fase de escala industrial (Mes 6+ del roadmap) y se justifique la inversión de ingeniería.
- **Test de validación:** N/A hasta que se decida investigar.

---

## Resumen de estado
| RR | Estado | Bloqueante para lanzamiento |
|---|---|---|
| RR-001 (firmware simulado) | **En progreso** — driver real escrito contra datasheet BMI270, sin validar (falta config file de Bosch + hardware físico) | Sí |
| RR-002 (precisión estimación FC) | Abierto | No (se lanza como "estimación") |
| RR-003 (coste batería IMU fino) | Abierto, pendiente de medición | No (se puede hacer opcional) |
| RR-004 (PPG descartado) | Cerrado por decisión de producto | No aplica |
| RR-005 (discrepancia consumo) | **Resuelto con datasheets reales** (era error propio de calibración) — pendiente solo de medición de banco para confirmar pérdidas de integración | No, ya no bloquea con las cifras recalculadas, pero conviene confirmar con banco antes de comprometer marketing definitivo |
| RR-006 (precisión GNSS no validada) | Abierto, pendiente de medición | Sí, para publicar precisión en marketing |
| RR-007 (pricing Plan Esencial) | **Cerrado (5€/mes)** | No, ya decidido |
| RR-008 (coste celda LiPo sin cotizar) | Abierto, requiere acción comercial | No, es optimización de margen, no bloqueante |
| RR-009 (ahorro módulo LilyGo, PCB propio) | Abierto, fuera de alcance por decisión | No, es oportunidad futura, no bloqueante |
