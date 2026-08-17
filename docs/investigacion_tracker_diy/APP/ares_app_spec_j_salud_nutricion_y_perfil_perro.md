# J) Salud / Nutrición / Perfil perro — Especificación (v1)

## Objetivo
Un módulo de salud y nutrición **fiable, honesto y accionable** que:
- Convierta actividad + perfil del perro en **objetivos diarios/mensuales**.
- Entregue **recomendaciones de comida en gramos** (y opcionalmente “tazas/puñados/cucharas” como traducción).
- Permita Q&A tipo “¿puede comer X?” con foco en **seguridad**.
- No haga promesas médicas: **orienta y advierte**, no “cura”.

Principio: **Backend = fuente de verdad** para métricas oficiales (kcal oficiales, flags, progreso) y para coherencia cross‑device.

---

## Alcance por plan (solo 2): Básico / Premium

### Básico (v1)
**Incluye (lo que se muestra):**
- Resumen diario: actividad (intensidad), descanso/inactividad, y “por debajo / igual / por encima” del objetivo del perro.
- Resumen semanal: “guardado semanal” (tendencia de actividad y descanso).
- Objetivo configurable (mantener / definir / perder grasa / ganar masa) **pero** el detalle nutricional se limita.

**No incluye:**
- Recomendación completa de ración/ingredientes.
- Q&A “¿puede comer X?”
- Suplementos.

### Premium (v1)
**Incluye todo**, con detalle:
- Calorías objetivo (DER) + ajuste por objetivo/BCS.
- Recomendación de comida **en gramos** (y equivalencias a tazas/cucharas si el usuario lo configura).
- Resumen diario y mensual avanzado.
- Q&A “¿puede comer X?”
- Suplementos y educación guiada (sin claims milagro).
- Registro de comidas (foto/etiqueta/casera) con control de cambios.

---

## Inputs del perfil del perro (onboarding)

### Capa 1 (rápida)
- Nombre
- Edad (meses o fecha nacimiento)
- Tamaño (toy/pequeño/mediano/grande/gigante)

### Capa 2 (precisión)
- Peso actual (kg)
- Altura (cm)
- Sexo
- Raza 1 (opcional)
- Raza 2 (opcional) + ratio mezcla (slider)
- Esterilizado (sí/no)

### Capa 3 (dieta habitual)
- Pienso / húmeda / mixta / casera cocida / BARF controlada

---

## Clasificación del perro + discrepancias (v1)
Se implementa **tal cual** la lógica de conciliación:
- Si difieren 1 “paso” (p. ej. pequeño vs mediano) y el usuario eligió uno → **respetar usuario** y marcar discrepancia leve.
- Si difieren ≥2 pasos → **proponer corrección** y marcar discrepancia fuerte.

### BCS objetivo
- Por defecto: **4–5**.
- Editable por Owner/Family (con guardarraíles: avisos si el objetivo es extremo).

### Estado de integridad
- ok / faltan_datos / datos_incongruentes.

---

## Objetivos del perro (v1)
El usuario define:
1) Objetivo principal:
- Mantener
- Definir (recomposición leve)
- Perder grasa
- Ganar masa/condición

2) “Exigencia” (slider):
- Menos exigente ↔ más exigente

El sistema devuelve:
- Objetivo diario
- Objetivo mensual
- Recomendación de “hoy toca”: más intensidad / más duración / más descanso

---

## Métricas de actividad y descanso (v1)

### Reglas de registro
- Se registra actividad **por minuto** (timeline) desde el primer movimiento.
- Se agrupa en “paseos/sesiones” según la lógica de sesiones ya definida.

### Outputs diarios (Básico + Premium)
- Minutos por intensidad (suave/moderada/vigorosa)
- Descanso/inactividad total
- Estado vs objetivo: por debajo / igual / por encima

### Outputs mensuales
- Progreso y tendencia (cumplimiento, consistencia, recuperación)

---

## Motor de calorías y ración (Premium v1)

### 1) Calorías objetivo (DER)
- Calcular RER.
- Aplicar factor de mantenimiento (DER = RER × factor).
- Ajustar según objetivo (pérdida/ganancia) y BCS.
- Autocalibración semanal si el peso/BCS se desvía del plan.

**Regla de seguridad:** si el sistema detecta señales de riesgo (BCS muy bajo, pérdida rápida, letargia marcada), se muestra aviso: “consulta veterinario”.

### 2) Recomendación de comida en gramos (v1)
**Siempre** recomendamos en **gramos**.

Para convertir kcal → gramos necesitamos la “referencia de comida”:
- **Pienso/comida comercial:** foto del saco/lata + lectura de kcal/100g (o entrada manual si falla).
- **Casera cocida:** receta base (ingredientes + gramos + rinde total). Si el usuario no quiere receta completa, se permite un “modo simple”: solo kcal estimadas y ración en gramos aproximados.

#### Equivalencias a tazas/cucharas/puñados (opcional)
- La app muestra **gramos** como principal.
- Además ofrece “traducción” si el usuario define su medida:
  - 1 taza = ___ g (se puede tomar de la etiqueta o calibrar una vez).
  - 1 cucharada = ___ g (si aplica).
  - Puñado = ___ g (aprox, calibración por usuario).

---

## Registro de comidas (Premium v1)
Cada registro incluye:
- Foto (opcional pero recomendado)
- Tipo: pienso/húmeda/mixta/casera
- Cantidad (g/ml)
- kcal estimadas (derivadas de la referencia)
- Notas (apetito/síntomas GI 24h)

### Control de cambios (clave)
- Owner/Family pueden cambiar la “comida base”.
- Temporal puede:
  - **ver** la comida recomendada esos días,
  - **registrar** comidas,
  - **marcar** “se cambió comida hoy” → queda como **pendiente de confirmación** por Owner/Family (para no romper cálculos sin control).

---

## Q&A “¿Puede comer X?” (Premium v1)

### Salida estándar
- Veredicto: **Seguro / Evitar / Tóxico**
- Motivo breve
- Qué hacer si ya lo comió
- Alternativas seguras

### Política de cantidades (tu decisión)
- **Tóxico / peligroso:** NO damos “cantidad segura”. Se responde **NO** y se dan pasos de acción.
- **Seguro / premios:** sí damos cantidades **orientativas** (en gramos) basadas en:
  - regla de “premios” (parte pequeña del total diario),
  - y tamaño/peso del perro.

### Ejemplos (para ilustrar el comportamiento)
**Ejemplo 1 (Tóxico): “¿Uvas/pasas?”**
- Respuesta: **TÓXICO**. No dar cantidad. Acción: registrar cantidad/tiempo si se sabe y contactar vet/poison control.

**Ejemplo 2 (Evitar): “¿Huesos cocidos?”**
- Respuesta: **EVITAR** (riesgo de astillas/obstrucción).

**Ejemplo 3 (Seguro como premio): “¿Zanahoria?”**
- Respuesta: **SEGURO**.
- Cantidad orientativa: gramos pequeños como snack (y el sistema lo descuenta del total diario).

---

## Suplementos (Premium v1)
Objetivo: ayudar a decidir **cuándo sí tiene sentido** y cuándo no.

### Reglas
- Siempre: “No sustituye veterinario ni medicación”.
- No se prometen curas.
- Se muestran **riesgos/interacciones** cuando aplique.

### Ejemplos (orientativos)
**Omega‑3 (EPA+DHA):**
- Uso típico: articulaciones, piel, inflamación (según contexto).
- Mostrar rango orientativo de dosis y avisar de precauciones (trastornos de coagulación, pancreatitis, etc.).

**Mitología que NO vendemos como real:**
- “Orégano/romero para desparasitar”: se etiqueta como **no sustituto** de antiparasitarios veterinarios. Puede mostrarse como “sin evidencia suficiente para reemplazar tratamiento”.

---

## Patologías (Premium v1) — sin diagnóstico ni tratamiento
No se introducen “patologías” como diagnóstico clínico en v1.

**Pero** sí se pregunta en Premium un “screen” de seguridad:
- “¿Tu perro tiene alguna condición diagnosticada o medicación?” (sí/no)
- Si sí: “Esto puede ser perjudicial” + ejemplos típicos de riesgos (sin afirmar curas).
- La app **evita recomendaciones** potencialmente peligrosas y deriva a “consulta vet”.

---

## UX mínimo (pantallas)

1) **Perfil del perro**
- Capa 1 / Capa 2 / Capa 3
- Discrepancias (chip de corrección)

2) **Objetivos**
- Selección objetivo + slider exigencia

3) **Resumen diario**
- Actividad vs objetivo
- Descanso/inactividad
- Recomendación de mañana

4) **Resumen mensual**
- Tendencia, consistencia, recuperación

5) **Comida (Premium)**
- “Comida base” (foto/etiqueta/receta)
- Recomendación en gramos + equivalencias
- Registro diario

6) **Q&A alimentos (Premium)**
- Buscar alimento
- Respuesta segura

7) **Suplementos (Premium)**
- Lista guiada
- Precauciones

---

## Backend / App — responsabilidades

### Backend (source of truth)
- Cálculo DER / kcal objetivo
- Cálculo ración en gramos (según referencia de comida)
- Consolidación de actividad (kcal oficiales)
- Flags de riesgo (BCS extremo, progresos raros, incoherencias)
- Motor Q&A (base de tóxicos + reglas)

### App
- Captura de inputs (foto/etiqueta)
- UI de objetivos
- Presentación de resúmenes
- Offline básico de últimos datos

---

## Guardarraíles (seguridad y confianza)
- Siempre distinguir: **estimado** (en vivo) vs **oficial** (backend).
- Copys: “Esto orienta; si hay síntomas o condición clínica, veterinario”.
- Para tóxicos: alerta roja + pasos + botón de llamada.

---

## Decision Log (J)
- **DL-J-001**: Solo 2 planes: Básico (resumen) / Premium (todo).
- **DL-J-002**: Premium incluye Q&A alimentos; en tóxicos NO se dan “cantidades seguras”.
- **DL-J-003**: Patologías no se registran como diagnóstico; sí hay pantalla de seguridad en Premium.
- **DL-J-004**: Recomendaciones siempre en **gramos**; equivalencias a tazas/cucharas son opcionales.
- **DL-J-005**: Temporal ve y registra comida durante su acceso; cambios de comida quedan “pendientes” de Owner/Family.

---

## Risk Register (J)
- **RR-J-001 (recomendación peligrosa por dato incorrecto):**
  - Mitigación: discrepancias + estado_integridad + avisos.
- **RR-J-002 (claims médicos):**
  - Mitigación: lenguaje no médico + derivación vet + no prometer curas.
- **RR-J-003 (conversión kcal→gramos sin datos de comida):**
  - Mitigación: exigir referencia (foto/etiqueta) o entrar en “modo simple” con precisión marcada.

---

## Próximo paso verificable (para QA)
1) Probar onboarding completo con 10 perfiles reales (mezcla razas, tamaños) y forzar discrepancias.
2) Probar recomendación de gramos con 3 escenarios:
   - pienso con kcal/100g,
   - húmeda,
   - casera simple.
3) Probar Q&A con 15 alimentos (incluye tóxicos) y confirmar que **nunca** damos “cantidad segura” en tóxicos.

