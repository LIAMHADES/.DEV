# ARES v4.0 — Backlog de Piezas Adicionales (Bloque D)
**Versión:** 1.0 | **Prioridad:** la más baja de las tres del proyecto, según orden confirmado por el usuario: (1) dispositivo/hardware/diseño/marca, (2) modelo de negocio, (3) funcionalidades y extras. Este documento cataloga las piezas de producto identificadas por el análisis competitivo que **no** se implementan en esta sesión — se registran para decidir en el futuro, una vez cerrada la base (Bloques A-C).

---

## Ya promovidas a la base del producto (no quedan en backlog)
- **Capa social/descubrimiento pet-friendly** (sitios que admiten perros, "pipicans", tips para dueños primerizos): promovida a `01_PRODUCTO_Y_NEGOCIO.md` §3.8 como pieza de producto aprobada, con enfoque recomendado (curado primero, comunidad después). Queda en fase de diseño, no de implementación, hasta que se cierren los Bloques 1 y 2 de prioridad.
- **Estimación de FC/esfuerzo vía IMU**: promovida a `SPEC_04_INTELLIGENCE_HEALTH.md` §1.4 (Bloque C de esta sesión).

## En radar, sin decisión de roadmap todavía

### 1. UWB para localización de precisión (~10cm)
- **Por qué importa:** el propio informe competitivo (`docs/Análisis Competitivo de Localizadores GPS para Perros (Europa).md`) señala esto explícitamente como diferenciador no explotado — ningún competidor analizado lo tiene.
- **Coste de explorar:** requiere nuevo módulo UWB en la BOM (cambio de hardware, similar en naturaleza a lo que se evaluó y descartó para PPG en RR-004) — no es una función de solo-firmware.
- **Recomendación:** mantener en radar. No es urgente porque ningún competidor lo tiene todavía (no hay presión competitiva inmediata), pero vale la pena revisitar cuando se cierre el Bloque de hardware/dispositivo (prioridad 1), ya que un cambio de antena/módulo afecta directamente al diseño físico.

### 2. Posicionamiento WiFi indoor (WPS)
- **Por qué importa:** Weenect e Invoxia lo ofrecen como fallback urbano/indoor; ARES solo usa WiFi para detección de zona segura y OTA.
- **Coste de explorar:** principalmente firmware (el WiFi ya está en el BOM) — no requiere cambio de hardware, a diferencia de UWB.
- **Recomendación:** de menor esfuerzo que UWB al no tocar hardware. Candidato razonable para una iteración de funcionalidades (prioridad 3) antes que UWB.

### 3. Detección de ladridos / micrófono
- **Por qué importa:** Tractive lo usa para detectar ansiedad/ladrido (parte de su propuesta de "salud emocional").
- **Coste de explorar:** requiere micrófono nuevo en la BOM — no está en el hardware actual. Cambio de hardware, no solo de firmware.
- **Recomendación:** mantener en radar, evaluar junto con UWB cuando se revisite el Bloque de hardware — ambas son adiciones de sensor, no de software.

### 4. Altavoz para reclamo de voz
- **Por qué importa:** feature de Pawfit (reproducir la voz grabada del dueño para calmar/llamar al perro).
- **Coste de explorar:** requiere altavoz nuevo en la BOM — cambio de hardware.
- **Recomendación:** menor prioridad que las anteriores — es una función de conveniencia, no de seguridad ni salud (los dos ejes centrales del producto según §1.5 de `01_PRODUCTO_Y_NEGOCIO.md`). Mantener en radar sin más acción por ahora.

## Resumen de priorización para cuando se llegue al Bloque de funcionalidades/extras (prioridad 3)

| Pieza | Requiere cambio de hardware | Alineada con eje "salud/bienestar" (§1.5) | Prioridad relativa sugerida |
|---|---|---|---|
| Social/descubrimiento pet-friendly | No | Sí (socialización/bienestar) | Ya promovida — primera a implementar |
| Estimación FC/esfuerzo vía IMU | No | Sí (salud) | Ya promovida — primera a implementar |
| Posicionamiento WiFi indoor (WPS) | No | No (es seguridad/localización) | Media — bajo coste, sin cambio de BOM |
| UWB precisión | Sí | No (es localización) | Media-baja — depende de revisión de hardware |
| Detección de ladridos/micrófono | Sí | Parcial (bienestar emocional) | Baja — depende de revisión de hardware |
| Altavoz reclamo de voz | Sí | No (conveniencia) | Baja — función de conveniencia, no core |

**Nota final:** ninguna de las piezas de este documento se implementa en esta sesión. Se registran aquí para que la próxima vez que el proyecto entre en la fase de "funcionalidades y extras" (prioridad 3, después de cerrar dispositivo y negocio), exista ya un punto de partida priorizado en vez de reabrir el análisis competitivo desde cero.
