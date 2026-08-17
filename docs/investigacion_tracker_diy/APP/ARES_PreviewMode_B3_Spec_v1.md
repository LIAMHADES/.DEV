# ARES — “Preview / Demo Mode” sin dispositivo (B3) (v1)
**Objetivo:** no es “usar el móvil como tracker”. Es un **modo de presentación y onboarding** para:
- explicar capacidades,
- elegir plan,
- canjear código,
- y preparar la app antes de que llegue el dispositivo.

---

## 1) Qué es (y qué NO es)
### Sí es
- Un **tour interactivo** (slider/cards) con:
  - geofence
  - ubicación
  - actividad orientativa
  - social (resumen)
  - nutrición (resumen)
- Una pantalla de **comparativa** de Plan Básico vs Premium.
- Un flujo de “**Ya tengo un plan**” → meter **código**.
- Un flujo “**Ya tengo cuenta**” → login y entrar.

### NO es
- Tracking real con el teléfono.
- Un modo que funcione como sustituto del hardware.
- Mapas offline descargables (por tu decisión).

---

## 2) Estructura B3 (dos niveles)

### Nivel 1 — Preview rápido (sin dispositivo)
**Entrada:** abrir app por primera vez (usuario nuevo).
1) Pantalla: “Crear cuenta / Iniciar sesión”
2) Tras crear cuenta: **Slider de capacidades** (cards con imagen + texto corto):
   - Ubicación (GPS)
   - Geofence + Modo Guardia
   - Modo Perdido
   - Luces
   - Actividad (orientativa)
   - Social (rankings/challenges – resumen)
   - Nutrición (resumen del “nutricionista” Premium)
3) CTA: “Continuar” → pantalla “Planes”

### Nivel 2 — Selección de plan + canjeo
Pantalla “Elige tu plan”
- Comparativa lado a lado (Básico vs Premium):
  - qué incluye cada uno (resumen)
  - precio
  - botón “Elegir”
- Acciones:
  - **Ya tengo un plan (código)** → input código → validar → activar plan
  - **Comprar plan** → (si se compra fuera en web, aquí solo se guía; si in-app purchase, procesar pago)
  - **Upgrade cuando quieras** (si empieza en básico)

---

## 3) Flujo “comprado en web antes de que llegue el dispositivo”
**Caso principal que quieres:**
- Usuario compra el plan en la web (básico por defecto).
- Al abrir la app:
  1) crea cuenta
  2) ve preview
  3) pulsa “Ya tengo plan” e introduce **código único**
  4) se activa el plan en backend
  5) queda listo para cuando llegue el tracker

**Cuando llega el dispositivo:**
- App muestra: “Vincula tu dispositivo”
- Emparejamiento y DeviceBinding (ver spec DeviceBinding).

---

## 4) Flujo “ya tengo cuenta”
- Pantalla inicial: “Ya tengo cuenta” → login.
- Si el usuario ya tiene perro(s), entra directo.
- Si tiene plan activo, ve la pantalla de “Vincular / Gestionar”.

---

## 5) Datos en Preview (cómo se simula)
- No hay dispositivo real, por tanto:
  - se usa un dataset **simulado** (perro demo) solo para UI
  - se bloquean acciones que consumen coste real (SMS/WhatsApp, Live real, etc.)
- El preview debe mostrar etiquetas claras:
  - “Ejemplo”
  - “Vista previa”
  - “Activa tu dispositivo para usarlo”

---

## 6) Reglas del Plan por defecto
- El usuario puede entrar sin elegir Premium.
- Por defecto:
  - se orienta al **Plan Básico** (porque es el mínimo)
  - Premium se presenta como upgrade en cualquier momento.

---

## 7) Offline maps
- **No disponible en Preview** (según tu decisión).

---

## 8) Objetivo de UX (para evitar confusión)
- El preview debe quedar claro como “explicación de capacidades”.
- La app no debe crear la expectativa de que “ya está trackeando” sin el tracker.

---

## 9) Copy mínimo recomendado (para que el usuario lo entienda)
- “Esta es una vista rápida de lo que podrás hacer con ARES.”
- “Cuando tu dispositivo llegue, podrás vincularlo en 2 minutos.”
- “¿Ya compraste un plan? Introduce tu código y deja todo listo.”
