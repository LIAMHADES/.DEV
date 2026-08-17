# ARES — Plan Básico (Standard) vs Plan Premium (Suscripción)
> Esta es la especificación completa de **qué incluye cada plan** y **cómo funciona**, basada en el listado que has enviado (considerado “todo lo que tenemos”).

---

## Principio de producto (importante)
- **No hay plan 100% gratuito**: el acceso al ecosistema requiere conectividad celular + nube, y ese coste (SIM/red, confirmado con 1NCE High Data: ~1,25€/mes a 250MB) es real y no puede eliminarse del todo — ver análisis de proveedor de red y consumo por fase de actividad.
- Existe un **Plan Esencial** de entrada, de coste mínimo, pensado para cubrir solo lo indispensable (localización fiable) al precio más bajo posible — en la práctica, tan cercano a “sin suscripción visible” como permite el coste real de datos. No es gratis, pero se diseña para sentirse como la opción más barata y sencilla del mercado.
- El **Plan Básico (Standard)** es el siguiente escalón y debe ser **muy completo** (seguridad + fiabilidad + experiencia) — ver contenido íntegro más abajo.
- El **Plan Premium** no “arregla” carencias críticas; añade **social avanzado, analítica, nutrición avanzada y recompensas**.

## Precios actualizados (v2.1 — 2026-08-14)

| Plan | Precio mensual | Precio anual | Cambio clave vs v2.0 |
|---|---|---|---|
| **Esencial** | **6€/mes** | 60€/año | Historial 7 días |
| **Básico** | **10€/mes** | 100€/año | Historial **30 días**, **5 zonas** seguras, **5 compartidos**, **informe de salud mensual** (PDF), **benchmarks por raza**, **historial de dietas y peso**, **guía de alimentos**, **informe de batería**, **score de bienestar diario**, **registro de medicación**, **guía de ejercicio** |
| **Premium** | **12,99€/mes** | 129,90€/año | Informe de salud **semanal** + **estadísticas diarias**, historial 1 año, nutrición IA, fatiga/edad/anomalías IA, **superalimentos**, **aviso de peligros de la zona**, **chat veterinario**, **plan de salud preventivo**, **modo cachorro/senior**, **análisis rascado/ladridos**, multi-mascota, rankings nacionales, Live Share, recompensas |

> **Exportación de datos (PDF + GPX):** incluida **por igual en Básico y Premium** — no es un diferenciador.
>
> **Qué diferencia Premium del Básico (v2.1):** la IA de nutrición (dieta personalizada + análisis de macros + **superalimentos**), la IA de salud (fatiga, recuperación, edad biológica, anomalías), el **aviso de peligros de la zona** (garrapatas, plantas venenosas, fauna según estación/ubicación), el historial de 1 año, multi-mascota, rankings nacionales, Live Share Pro, recompensas/eventos. El Básico cubre el "cuidado y conocimiento" (informes, benchmarks, dietas/peso, alimentos peligrosos); el Premium añade la **inteligencia que convierte los datos en decisiones** + **contenido exclusivo de nutrición y seguridad local**. 

> **Anclaje (anchoring):** Básico→Premium es solo +2,99€/mes. El Premium se percibe como "solo 3€ más" por mucho más valor (informe semanal, nutrición personalizada, multi-mascota, IA). El Esencial→Básico (+4€) queda justificado por el historial 30 días, 5 zonas, 5 compartidos e informe mensual.
>
> **Pago:** siempre vía **web** (evita el 15-30% de comisión de App Store / Google Play). Esto ahorra ~0,75-1,80€/mes de cada plan. Ver `ARES_Escalabilidad_Precios_Margenes.md` §4 (costes de servicio).

**Nota de reconciliación (higiene documental):** documentos anteriores (`01_PRODUCTO_Y_NEGOCIO.md`, `MARkETING.txt`) mencionaban una tabla “Freemium App | 0€ + 4.99€/mes” que contradecía el principio “no hay plan gratis” de este documento. Ambos se han alineado: no hay tier 0€, existe un Plan Esencial de bajo coste ligado al coste real de conectividad.

---

# 1) PLAN BÁSICO / STANDARD (muy completo)

## 1.1 Seguimiento y Seguridad
**Localización GPS en tiempo real**
- Ver ubicación en mapa con precisión disponible.
- Indicadores de **calidad de señal** y “edad del último fix” en dashboard.

**Modos de seguimiento inteligente (auto-adaptativo)**
- La frecuencia se ajusta automáticamente por actividad:
  - **Paseo (lento)**  
  - **Trote (medio)**  
  - **Carrera (rápido)**  
- Objetivo: equilibrar **batería** y **seguridad** sin que el usuario tenga que “pensar”.

**Modo Perdido (Live Tracking)**
- Activación manual desde app.
- Tracking de máxima frecuencia (aprox. cada 2–4 s) durante una **ventana limitada** (emergencias).
- Finalizada la ventana, vuelve al modo inteligente para proteger batería.

**Geofencing (Vallas Virtuales) — ampliado**
- Crear **hasta 5 zonas seguras** (ej. casa, parque, guardería, finca, casa de los abuelos).
- Alertas de entrada/salida.

**Geofencing adaptativo (“Modo Guardia”)**
- Si el perro se acerca al borde, el tracker sube automáticamente la frecuencia para avisar antes.
- Prioridad “seguridad” (geofence nunca queda ciega por ahorro).

**Find Nearby (Bluetooth)**
- Interfaz “frío/caliente” para encontrar al perro a corta distancia (hasta ~50 m, según entorno).

**Luces remotas**
- Encendido remoto de luces LED desde la app para localizarlo en la oscuridad.

**Alerta de caída o inmovilidad**
- Detección de posible emergencia si el dispositivo queda inmóvil tras un impacto (con umbral y ventana de tiempo definida por firmware).

**Cobertura de conectividad**
- Funcionalidad en **España/UE** o **Global** según el modelo adquirido (lo que se vende/activa en el dispositivo).

---

## 1.2 Fiabilidad y Conectividad
**Buffer Offline (Store & Forward)**
- Si se pierde cobertura (montaña/bosque), guarda la ruta en memoria interna.
- Al recuperar señal, sube automáticamente y la app muestra:
  - “Pendiente de sincronizar”
  - “Sincronizando”
  - “Sincronizado”

**Deep Sleep (ahorro por inmovilidad)**
- Si detecta inmovilidad prolongada (p. ej. >2 min), entra en consumo ultra-bajo.
- Mantiene latido/estado mínimo para no quedar “apagado” en silencio.

**Ahorro en Zonas Wi‑Fi Seguras**
- Si detecta una Wi‑Fi conocida (p. ej. “casa”), desactiva GPS automáticamente para ahorrar.
- **Requisito clave** (por tu feedback): debe existir **cambio manual de modo** desde la app para salir de ahorro y forzar tracking cuando se quiera.

---

## 1.3 Salud y Actividad (nivel básico)
**Clasificación de actividad**
- Distingue: reposo / caminar / trotar / correr.

**Ejercicio real (anti-trampa por vehículo)**
- Detecta viajes en coche/transporte y evita que esos km cuenten como actividad física.

**Temperatura ambiente**
- Monitoriza temperatura para alertas de riesgo por calor (contextual + umbrales).

**Alerta de golpe de calor (índice térmico real)**
- No solo temperatura ambiente: calcula el **índice térmico real** (temperatura + humedad) para avisar antes del riesgo.
- Incluido en **Básico y Premium** — es una alerta de seguridad crítica, no solo un extra.

**Recomendación de beber agua según los datos del perro**
- Sugerencias de hidratación basadas en intensidad/duración de actividad + temperatura + perfil del perro.

**Estimación genérica de calorías y distancia diaria**
- Cálculo básico visible en el dashboard.

**Estadísticas completas + benchmarks por raza**
- Desglose por tipo de actividad e intensidad, comparado con la media de su raza y edad.

**Guía de alimentos peligrosos y formación nutricional**
- Qué alimentos evitar (chocolate, uvas, etc.) y formación básica para dueños.

**Historial de dietas y peso**
- Registro de alimentación y peso para seguir la evolución.

**Informe explicativo de batería**
- Explica por qué la batería duró más o menos (cobertura, tracking intensivo, temperatura).

**Score de bienestar diario (0-100)**
- Un número simple que resume cómo está el perro hoy: actividad + descanso + temperatura + regularidad.
- Fácil de entender de un vistazo (el dueño no tiene que leer gráficos).

**Registro de medicación**
- Avisar cuándo toca cada medicación/tratamiento (calendario + notificación push).
- Complementa la guía de alimentos y el cuidado diario.

**Guía de ejercicio según raza/edad/peso**
- Minutos recomendados de ejercicio según el perfil del perro.
- Basado en la base de conocimiento canina (ver `docs/combers`).

---

## 1.4 Interfaz y Experiencia de Usuario
**Historial de rutas (30 días)**  
- Acceso al último mes de rutas/ubicaciones.

**Informe de salud mensual (PDF)**  
- Resumen automático mensual de: actividad, descanso, peso, tendencias y alertas.
- Formato: PDF, resumen listo para leer o compartir.

**Exportación de datos (PDF + GPX)**
- Descargar el historial de rutas y los datos como **PDF** o **GPX** (para apps deportivas).
- Incluido por igual en **Básico y Premium**.

**Dashboard principal**
- Ubicación
- Estado (movimiento/reposo)
- Batería
- Calidad de señal

**Alertas Push**
- Salida/entrada geofence
- Batería baja
- Estados críticos relevantes

**Alertas por SMS / WhatsApp (básicas)**
- Envío de alertas esenciales de geofence por canal alternativo (con cupo/uso razonable para controlar coste).

**Mapas offline (España)**
- Uso de mapas sin conexión para visualizar y navegar.

**POIs (Puntos de interés)**
- En mapa: parques, fuentes, veterinarios, etc.

**Normativa de área (contextual)**
- Alertas si se entra en zona con reglas específicas (ej. playas con restricción en verano).

---

## 1.5 Social (básico)
**Compartir con familia y amigos (ampliado)**
- Hasta **5 usuarios** incluidos.
- Permisos: **Propietario / Admin / Invitado**.

**Rankings de actividad (local)**
- Ranking semanal (local).

> **Nota sobre la tienda integrada:** la **tienda de bienestar** está planificada como **modelo dropshipping (intermediario)**: el usuario ve y compra desde la web/app de ARES, ARES pide las unidades al fabricante (sin stock propio) y el producto llega directo al cliente. NO se lanza en esta fase — requiere curaduría y partners. Plan completo en `ARES_Tienda_Integrada_Bienestar.md`. En la web no aparece en la tabla de precios hasta que esté lista.

---

# 2) PLAN PREMIUM (Suscripción avanzada)

> Premium amplía el ecosistema: **social serio**, **analítica**, **salud avanzada** y, especialmente, **nutrición (“nutricionista” en la app)**.

## 2.1 Social y Competitivo (avanzado)
**Gestión multi-mascota**
- Añadir y gestionar varios perros/dispositivos en una sola cuenta.

**Compartir ampliado (+ de 2 usuarios)**
- Añadir más usuarios con roles (Propietario/Admin/Invitado).
- Ideal para familias grandes, cuidadores, paseadores, etc.

**Rankings avanzados**
- Rankings **nacional** y **por raza**:
  - mensual
  - trimestral
  - anual

**Rutas de amigos**
- Visualización de rutas y tiempos de amigos en tu red.

**Grupos y desafíos**
- Crear/unirse a grupos locales y participar en challenges (semanales/mensuales).
- Ej.: “El perro que más corre en Madrid este mes”.

**Eventos VIP**
- Acceso a eventos/desafíos especiales.

---

## 2.2 Análisis Avanzado y Datos
**Historial extendido**
- Escala desde 30 días hasta **1 año** completo en la nube (según configuración del plan).

**Informe de salud semanal (PDF) + estadísticas diarias**
- Resumen automático semanal de actividad, descanso, peso y tendencias.
- **Estadísticas diarias en la app:** cómo va el perro hoy (actividad, comidas registradas, peso, descanso) — pensado para quien registra comidas a diario.

**Exportación de datos**
- Exportar historial como **PDF** o **GPX** (para apps deportivas).
- *(Igual que en Básico — incluida por igual en ambos planes.)*

**Estadísticas completas de salud**
- Desglose por tipo de actividad, intensidad y benchmarks por raza.

**Fatiga y recuperación (IA)**
- Estimaciones de estado de forma basadas en histórico.
- Recomendaciones de carga/descanso.

**Anomalías de comportamiento**
- Alertas por cambios en patrones de actividad o descanso (p. ej. noche más inquieta).

**Análisis de comportamiento avanzado (rascado, ladridos)**
- Detección y seguimiento de **rascado** y **ladridos** como señal de posibles problemas (alergias, picaduras, molestias).
- *(La "ansiedad por separación" queda fuera — complejidad y fiabilidad de detección no justificadas.)*

**Edad biológica**
- Métrica que compara actividad con media de raza y edad.

**Chat/triaje con veterinario (texto)**
- Consulta por chat con un veterinario (partner) o triaje asistido por IA.
- El problema más valorado por los dueños; enorme retención y confianza.

**Plan de salud preventivo personalizado**
- Vacunas, desparasitación, chequeos y cuidados según el perfil del perro (raza/edad/estilo de vida).
- Lleva los "recordatorios de cuidados" a un plan estructurado y adaptado.

**Alerta de golpe de calor específica (índice térmico real)**
- No solo temperatura ambiente: calcula el **índice térmico real** (temperatura + humedad) para avisar antes del riesgo.
- *(La alerta de golpe de calor está incluida en **Básico** — ver §1.3. En Premium se amplía con más contexto histórico y avisos personalizados.)*

**Modo cachorro / senior**
- Metas y avisos adaptados a la etapa de vida (actividad, descanso, alimentación, límites).
- Diferencia el producto por etapa de vida del perro.

---

## 2.3 Salud y Nutrición (Dog Fuel Avanzado) — “premium = nutricionista”
**Calorías y macronutrientes (preciso)**
- Recomendación de ingesta calórica y reparto proteína/grasa según:
  - perfil del perro (raza/edad/peso/objetivo)
  - actividad real (lo que de verdad hace)
- Ajuste continuo: si cambia la actividad real, cambia el “plan de comida”.

**Base de datos de alimentos + guía de superalimentos**
- Acceso a catálogo con recomendaciones personalizadas.
- Sugerencias de alternativas por objetivos (bajar peso, rendimiento, mantenimiento).
- **Guía de superalimentos y alimentos óptimos** para la mascota (qué es realmente bueno, no solo qué evitar).

**Historial de dietas y peso**
- Registro de alimentación y peso para seguir evolución.

**Dog Fuel básico (identificación rápida de alimentos)**
- Escáner de código de barras o foto para identificación básica de productos/alimentos.

**Aviso de peligros de la zona (según estación y ubicación)**
- Avisa de riesgos ambientales locales según la ubicación y la época del año: garrapatas, plantas venenosas, fauna peligrosa (víboras, jabalíes), heladas/calor extremo, etc.
- Fuente de contenido a validar con veterinarios; se publica con disclaimer de "recomendación, no diagnóstico".

---

## 2.4 Recompensas y Gamificación (Rewards)
**Recompensas ampliadas**
- Cupones y beneficios exclusivos por hitos de actividad.

**Insignias y logros**
- Badges por completar desafíos o alcanzar objetivos.

---

## 2.5 “Explicabilidad” (para reducir quejas y soporte)
**Informe de batería**
- Explica por qué la batería duró más o menos:
  - mala cobertura
  - uso intensivo de tracking
  - temperatura
  - etc.

---

## 2.6 Seguro (integración en ecosistema) — pendiente de detalle
> No has pegado el detalle exacto del seguro, pero lo incluyes como requisito. Para que no falte en la propuesta:

**Seguro integrado (Premium o Add-on)**
- Acceso a productos de seguro para mascota desde la app:
  - comparación/contratación (si aplica)
  - gestión básica (póliza, documentos)
  - recordatorios y soporte
- **Nota**: coberturas/condiciones dependen del partner y deben definirse en un anexo.

---

# 3) Add-ons recomendados (sin 3er plan)

## 3.1 Travel / Fuera de país (toggle)
**Objetivo:** habilitar conectividad fuera de la “zona base” sin obligar a cambiar de plan.

**Precios**
- **UE/EEE Pass:** **5,99 €/mes** o **2,99 €/semana**
- **Global Pass:** **9,99 €/mes** o **4,99 €/semana**

**Qué incluye**
- Cobertura/roaming habilitado **fuera de la zona base** (definir base: UE/EEE o país de compra, según acuerdos SIM).
- Priorización de red/operador y validación extra de conectividad para reducir “sustos” (mejor feedback de estado).

**Regla de pricing**
- El Travel debe cubrir el **coste SIM real** fuera de la zona base. Si el coste fuera UE se dispara, se ajusta el **precio del add‑on**, no el plan principal.

## 3.2 Seguro (pago separado)
**Modelo de precio acordado**
- **Seguro base de 2 años:** **50% del precio del dispositivo** (pago único). La cobertura mínima es de 2 años, pero se adaptará a la duración obligatoria por ley en cada país (ej. 4 años en España).

> Nota: el detalle de coberturas y partner del seguro debe definirse en un anexo (sin inventar coberturas aquí).

## 3.3 Historial extendido (upsell desde Básico)
- Si alguien está en Plan Básico: **Historial 365 días** por **+2,99 €/mes**.

## Add-on: **Búsqueda colaborativa avanzada (Live Share Pro)**

### Objetivo

Permitir que **más personas ayuden a encontrar al perro en tiempo real**, sin aumentar el consumo de batería del dispositivo y manteniendo **control total de privacidad** por parte del Owner. Este add-on está disponible para usuarios del Plan Básico que deseen las funcionalidades extendidas.

---

## Disponibilidad por plan

### Plan Básico (incluido)

* **Compartir búsqueda activa hasta 12h**.
* **Hasta 2 ayudantes invitados** simultáneos.
* Acceso de ayudantes:

  * Solo **ubicación en vivo del perro**.
  * Mapa simplificado en la app (Guest Mode).
  * Sin histórico, sin rutas, sin datos de salud, sin ajustes.
* Invitación mediante **enlace temporal** (deep link).
* Caducidad automática a las **12h** o revocable por el Owner en cualquier momento.

### Plan Premium (incluido)

* **Live Share Pro está incluido en el Plan Premium**. Permite:
  * **Compartir búsqueda activa hasta 12h** (renovable).
  * **Hasta 10 ayudantes invitados** simultáneos.
  * Todo lo incluido en Básico, más:
    * Mejor coordinación de equipos grandes (familia, vecinos, voluntarios).
    * Prioridad en frecuencia de actualización (dentro de límites de batería).
    * Mismo modelo de privacidad y control.

---

## Precio del Add-on

* **Live Share Pro (para Plan Básico)**: **+2,99 €/mes**
  (suscripción mensual, sin pagos por activación, solo para usuarios del Plan Básico que desean la funcionalidad extendida)

### Justificación de precio

* Coste operativo máximo estimado: **< 0,50 €/mes por usuario** incluso en escenarios extremos.
* Margen amplio y sostenible.
* Evita fricción en momentos críticos (no se cobra por evento de pérdida).
* Precio psicológico bajo y aceptable en Europa.

---

## Funcionamiento técnico (resumen contractual)

* El **dispositivo envía su ubicación una sola vez a la central**, según la cadencia definida por el Owner (hasta 10% de batería; después decide el dispositivo).
* La **central reemite esa misma ubicación** a todos los móviles autorizados.
* **El número de ayudantes NO incrementa**:

  * el consumo de batería del dispositivo,
  * ni la frecuencia de envío desde el tracker.
* Los ayudantes solo reciben datos **read-only**.

---

## Modo Invitado (Guest Mode)

Los ayudantes que acceden mediante enlace:

* **No necesitan credenciales**.
* Entran directamente a un **modo de mapa rápido** en la app.
* Pueden ver:

  * Ubicación actual del perro.
  * Su propia ubicación (para orientarse).
* **No pueden**:

  * Ver rutas pasadas.
  * Cambiar configuraciones.
  * Acceder a salud, sesiones, social o cuenta.

---

## Seguridad y privacidad (GDPR)

* Enlaces con **token aleatorio no adivinable**.
* Caducidad automática (12h).
* Revocación inmediata por el Owner.
* Límite de ayudantes simultáneos según plan.
* Aviso explícito en UI:

  > “Comparte este enlace solo con personas de confianza. El acceso caduca automáticamente.”

---

## Mensaje de valor (para UX / marketing interno)

> “Cuando tu perro se pierde, cada minuto cuenta.
> Con Live Share Pro puedes coordinar a todo tu equipo en tiempo real,
> sin gastar más batería y con control total de privacidad.”

---

## Decision Log (Upsell)

* **DL-L-UP-001**: El upsell se basa en **número de ayudantes**, no en duración.
* **DL-L-UP-002**: Precio fijo mensual (no pago por evento).
* **DL-L-UP-003**: El upsell no afecta al consumo del dispositivo.
* **DL-L-UP-004**: Invitados siempre en modo read-only y sin credenciales.

---



# 4) Reglas de diseño obligatorias (aprendidas del dolor Tractive)
- **Cambio manual de modo** siempre disponible desde app (salir de Wi‑Fi ahorro → tracking inmediato).
- El dispositivo **nunca** debe quedar en “ningún modo” mientras haya batería.
- Geofence debe mantener **prioridad de seguridad** incluso en ahorro.
- UX: home con 3 respuestas claras: **dónde está**, **qué modo**, **qué autonomía**.
