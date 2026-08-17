# ARES — Especificación DeviceBinding (v1)
**Objetivo:** definir con precisión cómo funciona el **vínculo Dispositivo ↔ Perro ↔ Usuarios**, incluyendo transferencias, invitaciones temporales y logs (auditoría).

---

## 1) Entidades y conceptos

### 1.1 Perro (Dog Profile) = “cuenta” de datos
- Un **Perro** es una entidad independiente que guarda:
  - Perfil (nombre, raza, edad, peso, objetivos, etc.)
  - Historial (rutas, actividad, métricas, nutrición si aplica)
  - Configuración (geofences, POIs, normativa, alertas)
- **Regla clave:** el histórico pertenece al **perro**, no al dispositivo ni al teléfono.

### 1.2 Dispositivo (Tracker) = hardware intercambiable
- Un **device_id** (tracker físico) se puede:
  - vincular a un perro
  - desvincular
  - reemplazar por otro tracker sin perder datos del perro

### 1.3 DeviceBinding
- Un DeviceBinding representa: **device_id → dog_id** con estado.
- **Regla:** 1 dispositivo solo puede estar vinculado a **1 perro activo** a la vez.
- **Historial de bindings**: se guardan eventos de vinculación/desvinculación.

### 1.4 Usuarios y roles (por perro)
- **Owner principal**: primer usuario que configura el dispositivo.
- **Owner secundario** (gratis, incluido en Plan Básico): segundo propietario con casi los mismos poderes.
- **Caregiver / Invitado temporal**: acceso limitado y con caducidad.

---

## 2) Permisos (ACL) por rol

### 2.1 Owner (principal y secundario)
Puede:
- Ver ubicación y estado del tracker
- Cambiar modos (incl. Modo Perdido)
- Encender luces
- Configurar y editar geofences
- Invitar / revocar caregivers
- Añadir / quitar owner secundario
- Desvincular / reemplazar dispositivo
- Iniciar “Transferencia de propiedad” (entre cuentas)
- Ver logs completos del perro

### 2.2 Caregiver / Invitado temporal
Puede:
- Ver ubicación / estado
- Ver información básica de seguridad (geofence, batería, señal)
- **Activar Modo Perdido** (Live Tracking) **pero**:
  - notifica inmediatamente a los Owners (push + log)
- Encender luces
- Recibir alertas (push) relacionadas con seguridad del perro

No puede:
- Editar geofences
- Desvincular / transferir dispositivo
- Añadir/quitar usuarios
- Cambiar “cuenta del perro” o datos sensibles (según definas)

---

## 3) Reglas de invitaciones

### 3.1 Owner secundario (gratis)
- Máximo: **1 owner secundario** incluido en Plan Básico.
- Alta:
  1) Owner principal invita (email/teléfono)
  2) Invitado acepta
  3) Queda como Owner secundario
- Baja:
  - Cualquiera de los Owners puede retirar al otro Owner (con confirmación fuerte).

### 3.2 Caregiver temporal
- Lo crea un Owner desde “Compartir → Añadir cuidador”.
- **Duración**: definida por Owner, máximo **1 mes**.
- Revocación: instantánea (Owner puede quitar acceso cuando quiera).
- Los Owners ven:
  - cuándo aceptó
  - cuándo expira
  - qué acciones críticas ejecutó (logs)

> Nota (técnica): la app debe mostrar claramente “Acceso temporal hasta: fecha/hora”.

---

## 4) Flujos (pantallas + comportamiento)

### 4.1 Primera configuración (binding inicial)
**Precondición:** usuario tiene cuenta (o se crea) y está logueado.
1) Emparejar por BLE (o método definido) y validar el tracker.
2) Seleccionar/crear Perro.
3) Backend crea:
   - DogProfile (si no existía)
   - DeviceBinding: `ACTIVE`
   - Owner principal = usuario actual
4) App muestra Dashboard del perro.

**Log:**
- `DEVICE_BOUND` (device_id, dog_id, by_user, timestamp)

---

### 4.2 Reemplazo de dispositivo (GPS nuevo) sin perder datos
1) Pantalla “Dispositivo → Cambiar dispositivo”
2) Confirmación fuerte (PIN/biometría)
3) `UNBIND` del dispositivo actual (o marcarlo como reemplazado)
4) Emparejar nuevo tracker
5) `BIND` al mismo dog_id

**Resultado:**
- Historial del perro intacto
- Cambia solo el device_id activo

**Logs:**
- `DEVICE_UNBOUND`
- `DEVICE_BOUND`
- `DEVICE_REPLACED` (opcional, para agrupar el evento)

---

### 4.3 Cambio de teléfono
- El usuario inicia sesión en el móvil nuevo.
- Accede al perro y a todo su historial (perro es independiente del teléfono).
- Si además quiere dar acceso a otra persona, usa “Compartir”.

**Log:**
- `LOGIN_NEW_DEVICE` (opcional; útil para seguridad)

---

### 4.4 Transferencia de propiedad (cuenta a cuenta) — Opción 3 (modo transferencia + espera + confirmación)
**Objetivo:** permitir segunda mano / traspaso sin soporte, de forma controlada.

**Reglas:**
- Requiere:
  - activar “Modo transferencia”
  - esperar un tiempo **configurable** (por producto, ej. 24h por defecto)
  - confirmación (email/OTP)
- No permitido si:
  - el perro/dispositivo está en Modo Perdido activo (anti-robo), salvo soporte interno.

**Flujo:**
1) Owner activa “Transferir”
2) App indica: “Transferencia pendiente, finaliza en X horas”
3) Se envía código / link al nuevo owner
4) Nuevo owner acepta
5) Se reasigna ownership y se cierra el binding anterior (o se mantiene dog_id según tu estrategia de “venta con perro”)

**Logs:**
- `TRANSFER_REQUESTED`
- `TRANSFER_CONFIRMED_OWNER`
- `TRANSFER_ACCEPTED_NEW_OWNER`
- `TRANSFER_COMPLETED`

---

## 5) Logs (auditoría) — eventos mínimos obligatorios
- `DEVICE_BOUND`
- `DEVICE_UNBOUND`
- `DEVICE_REPLACED`
- `OWNER_INVITE_SENT`
- `OWNER_INVITE_ACCEPTED`
- `OWNER_REMOVED`
- `CAREGIVER_INVITE_SENT`
- `CAREGIVER_ACCEPTED`
- `CAREGIVER_REVOKED`
- `CAREGIVER_EXPIRED`
- `MODE_CHANGED` (incluye: Live/Lost/Home Save/Tracking)
- `LOST_MODE_TRIGGERED_BY_CAREGIVER` (con notificación a owners)
- `GEOFENCE_EDITED` (solo owners)
- `LIGHTS_TRIGGERED`
- `PLAN_REDEEMED` (código)
- `TRANSFER_*` (si aplica)

**Visibilidad:**
- Owners: ven el log completo.
- Caregiver: no ve logs (o solo mínimos si decides).

---

## 6) Notificaciones
- Si caregiver activa Modo Perdido:
  - push inmediato a Owners: “Cuidador X activó Modo Perdido”
  - evento en logs
- Eventos críticos (geofence, batería baja, offline prolongado) → push (según settings).

---

## 7) Monetización / estructura de cuentas (según tu criterio)
- **Un perro = una “cuenta/perfil”**. Si se quiere gestionar otro perro con su propio dispositivo, es una **cuenta adicional** (de pago según tu modelo).
- Reemplazo de tracker no crea un perro nuevo: se mantiene dog_id.

---

## 8) Parámetros cerrados
- **Máximo caregivers simultáneos:** **3**.
- Si caregiver activa **Modo Perdido**:
  - Notificación **push** inmediata a Owners.
  - Si el Owner tiene **SMS/WhatsApp** activado, también se envía por esos canales.
