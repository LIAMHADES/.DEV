# K) Notificaciones y canales — Especificación (v1)

## Objetivo
- Notificar **rápido** y con **alta probabilidad de lectura** sin arruinar UX ni costes.
- Push es el canal base siempre.
- Premium añade WhatsApp **solo** donde aporta valor (geofence) y con control de costes.
- Email se usa para **marketing/educación/updates**, no para emergencias.

Fuentes:
- App spec: Push como base; canales extra pendientes por tier. fileciteturn13file10
- Funcionalidades: Matriz/tabla de alertas por tipo/canal/tier. fileciteturn13file15

---

## Canales v1

### 1) Push (FCM) — siempre
- Canal principal para todas las alertas operativas.
- Debe soportar: deep link a pantalla de evento, “ack/visto”, y acción rápida si aplica.

### 2) Bandeja in‑app (Eventos) — siempre
- Historial de alertas con:
  - timestamp, severidad, motivo, datos relevantes, y estado (visto/ack).
- Evita soporte y “¿qué pasó?”.

### 3) WhatsApp — solo Premium (opt‑in)
- Se usa **solo** para:
  - **Geofence EXIT** (y opcional ENTER si el usuario lo activa).
- No se usa para batería, calor, inmovilidad, etc.

### 4) Email — solo marketing / comunicación (no alertas críticas)
- Campañas, descuentos, novedades, contenidos educativos.
- (Opcional futuro) reportes mensuales si el usuario lo activa.
- No se usa para geofence ni pérdida de señal.

### 5) SMS — fuera de v1
- No se implementa en v1 por coste/operación.

---

## Planes (solo 2): Básico / Premium

### Básico
- Push + in‑app.
- Sin WhatsApp.
- Email solo marketing (si el usuario lo consiente).

### Premium
- Push + in‑app.
- WhatsApp (opt‑in) **solo geofence**.
- Email marketing (si consiente).

---

## Tipos de alertas (v1) y canales

### A) Geofence
#### 1) GEOFENCE_EXIT (crítica)
- **Push:** Básico + Premium.
- **WhatsApp:** Premium (opt‑in) con escalado (ver “Modo B”).
- **Email:** NO.

#### 2) GEOFENCE_ENTER (informativa)
- **Push:** Básico + Premium (configurable).
- **WhatsApp:** Premium (opcional, por defecto OFF).

**Rate limit:**
- No repetir EXIT hasta que haya RE‑ENTER o pasen X minutos (p. ej. 10 min) + histéresis.

---

### B) Pérdida de señal / pérdida de tracking
**Definición:** si el backend no recibe heartbeat/posición durante un intervalo.

- Trigger v1: **60 s** sin comunicación con backend.

**Canales:**
- **Push:** Premium (sí). Básico (no).
- **WhatsApp:** NO.
- **Email:** NO.

**Mensaje (copy honesto):**
- “Sin señal desde hace 60 s. La posición puede no ser exacta hasta que reconecte. Última ubicación: …”.

**Rate limit:**
- 1 push al iniciar.
- Recordatorios cada 30–60 min (solo si persiste y configurable) — Premium.

---

### C) Batería
**Canales:**
- **Push:** siempre (Básico + Premium).
- **WhatsApp:** NO.
- **In‑app:** indicador visible cuando <15%.

**Umbrales (confirmado):**
- 20% (baja) → 1 push.
- 10% (crítica) → 1 push.
- 5% (muy crítica) → 1 push.

**Regla anti‑spam:** no repetir por % intermedios.

---

### D) Riesgos ambientales (educación + seguridad)

#### 1) Calor / golpe de calor (riesgo)
- **Push:** siempre.
- Mensajes guiados (contexto + acción):
  - “Evita salir 12:00–15:00. Prioriza sombra y baja intensidad.”
  - Si se detecta actividad sostenida durante calor: a los 20 min otro push:
    - “Humedece el cuerpo (no el hocico). No dejes beber en exceso de golpe.”

**Nota de producto:** el copy debe ser responsable y no médico; objetivo: prevención.

#### 2) Asfalto caliente (ciudad)
- Trigger: exposición/tiempo en exterior + condiciones de calor.
- Push tras ~1h en calle con condiciones de riesgo:
  - “Riesgo de asfalto caliente: puede quemar almohadillas. Busca césped/sombra.”

**Rate limit:** máximo 1–2 al día por tipo con histéresis.

---

### E) Golpe / impacto e inmovilidad

#### 1) Impacto fuerte
- **Push:** siempre.
- Trigger: golpe fuerte + no movimiento durante **15 s**.
- Copy:
  - “Posible golpe fuerte. Si (mascota) no se mueve, revisa ahora.”

#### 2) Inmovilidad anómala (futuro / Premium si aplica)
- Si se implementa en v1: Premium push.
- Si no: v1.1.

---

### F) Logros / engagement
- **Push:** siempre, pero se recomienda digest (diario).

---

## Modo de escalado Premium para WhatsApp (decisión final)

### Modo B (elegido): Push primero + WhatsApp si no hay ACK
- Para **Geofence EXIT**:
  1) Push inmediato.
  2) Si el usuario **no abre la app / no hace ACK** en **30 s**, enviar WhatsApp.

**Requisito:**
- La notificación push y la bandeja in‑app deben permitir “Marcar como visto / ACK”.

---

## Preferencias y roles

### Roles (consistentes con H/I/J)
- **Owner + Family:** reciben push y pueden configurar preferencias.
- **Temporal:** recibe push/in‑app durante su ventana de acceso.
  - WhatsApp: no (evita coste/abuso). *(Ajustable si lo pides más adelante.)*

### Preferencias por usuario y por perro
- Configuración granular (ON/OFF por tipo de alerta) con defaults seguros.

---

## Anti‑abuso (backend)
- Cooldowns por tipo de alerta.
- Histéresis en umbrales (evita “flapping”).
- Dedupe de eventos: no mandar la misma alerta si no cambió el estado.

---

## Ejemplos v1 (texto real de notificación)

1) **Geofence EXIT (push)**
- “(Mascota) salió de la zona segura. Última ubicación: …”

2) **Geofence EXIT (WhatsApp Premium, si no ACK en 30 s)**
- “Alerta: (Mascota) salió de la zona segura. Abre ARES para ver ubicación.”

3) **Pérdida de señal (Premium push, 60 s)**
- “Sin señal desde hace 60 s. La posición puede no ser exacta hasta reconectar.”

4) **Batería 10% (push)**
- “Batería crítica (10%). Activa ahorro o carga el dispositivo.”

5) **Calor (push educativo)**
- “Evita salir 12:00–15:00. Sombra y baja intensidad.”

6) **Asfalto caliente (push)**
- “Riesgo de asfalto caliente: puede quemar almohadillas. Busca césped/sombra.”

7) **Impacto + inmóvil 15 s (push)**
- “Posible golpe fuerte. Revisa a (Mascota) ahora.”

---

## Decision Log (K)
- **DL-K-001**: Push + in‑app siempre.
- **DL-K-002**: WhatsApp solo Premium y solo geofence.
- **DL-K-003**: Email no se usa para alertas críticas; solo marketing/updates.
- **DL-K-004**: Pérdida de señal: Premium push a los 60 s (sin WhatsApp).
- **DL-K-005**: Batería: push 20/10/5% + indicador in‑app <15%.
- **DL-K-006**: Modo B: WhatsApp si no ACK en 30 s.

---

## Risk Register (K)
- **RR-K-001 (spam / fatiga):** demasiados pushes.
  - Mitigación: cooldowns, histéresis, digests, preferencias.
- **RR-K-002 (coste WhatsApp):** mensajes innecesarios.
  - Mitigación: Modo B con ACK + solo geofence.
- **RR-K-003 (mensajes de salud demasiado “médicos”):** riesgo legal/confianza.
  - Mitigación: copy preventivo, no diagnóstico, derivación vet si aplica.

---

## QA / Tests mínimos
1) Geofence EXIT: push inmediato + WA tras 30 s sin ACK.
2) Pérdida señal: dispara a 60 s, no se repite sin estado.
3) Batería: notifica solo en 20/10/5 y muestra banner <15.
4) Calor/asfalto: histéresis + no spam (máximo 1–2/día).
5) Impacto: evento + verificación de inmovilidad 15 s.

