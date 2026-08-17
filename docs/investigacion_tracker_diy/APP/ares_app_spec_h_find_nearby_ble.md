# H) Find Nearby (BLE) — Especificación cerrada (v1)

## Objetivo
Permitir encontrar el dispositivo/perro a corta distancia (casa, parque, ciudad cuando ya estás cerca) usando Bluetooth Low Energy (BLE) con un flujo rápido, honesto y con consumo controlado. **No es direccional** (sin flechas), es **hot/cold RSSI**.

---

## Decisiones v1 (congeladas)
- **Experiencia**: Hot/Cold RSSI (sin guía direccional).
- **Coded PHY (BLE Long Range)**: **Solo en “Find Activo”**.
- **BLE Standby**: **Por ventanas (modo B)** para compatibilidad con reposo/ahorro.
- **Latencia objetivo** (detección al abrir Find Nearby): **≤ 5 s**.
- **LED Find**: patrón distinto a LOST_MODE y **limitado por batería (Plan 2)**.
- **PING**: incluye **micro-destello**.
- **Emparejamiento/transferencia**: sin botón físico; **dock magnético (carga) como método principal**, y **patrón de luces como fallback**.
- **Caducidad de invitación temporal**: por defecto **24h**, pero **el Owner decide** (puede ajustar por invitación).

---

## UX (App)
### Pantalla “Find Nearby”
1) **Estado de enlace**: Conectando / Conectado / Señal débil.
2) **Radar hot/cold**:
   - Frío (lejos), Tibio (cerca), Caliente (muy cerca).
   - Mostrar tendencia (↑ / ↓) basada en filtro (mediana/EMA) para evitar saltos.
3) **Botón “Hacer parpadear”** (LED Find) con temporizador y aviso de batería.
4) **Botón “Ping”** (confirmación + micro-destello).
5) **Batería del tracker** (lectura rápida).
6) Mensaje honesto: “La señal es aproximada. En interior puede rebotar; muévete y observa la tendencia”.

### Comportamiento recomendado al usuario
- Si no sube la señal: caminar en arco/círculo (reduces rebotes y orientaciones malas).
- En interior: acercarse a zonas altas/ventanas, reducir interferencias.

---

## BLE: Modos y consumo (diseño)
### 1) BLE Standby (ventanas) — siempre disponible sin “radio constante”
**Propósito**: que el móvil detecte el tracker en ≤5 s aunque esté en reposo.

**Estrategia**:
- En reposo, el dispositivo hace micro-wake para anunciar BLE y vuelve a dormir.
- Parámetros iniciales para cumplir 5 s:
  - Periodo de ventana: **cada 4 s**
  - Duración de ventana: **500 ms** de advertising
  - Advertising connectable
  - Potencia TX: baja/media (ajustable tras medición)

**Nota**: parámetros ajustables tras test de consumo/latencia.

### 2) Find Activo (solo cuando el usuario abre Find Nearby)
**Propósito**: actualización rápida y estable de RSSI.

- Se activa al entrar en pantalla Find Nearby.
- Activa **Coded PHY** si el móvil lo soporta.
- Connection interval inicial: **250 ms** (ajustable si se requiere más fluidez).
- Timeout de sesión: configurable (recomendado 5 min máx por sesión).

---

## Comandos BLE (v1)
### Permitidos (solo “encontrar”)
- **RSSI hot/cold**: lectura RSSI y cálculo de estado Frío/Tibio/Caliente.
- **LED_FIND_START / LED_FIND_STOP**: patrón de búsqueda.
- **PING**: ACK + micro-destello.
- **READ_BATTERY**: batería % (y opcional temperatura si está disponible).

### Prohibidos por BLE (v1)
- Cambiar modos GNSS, activar LOST_MODE, OTA, cambios persistentes críticos.

---

## Permisos (roles)
### Owner
- Control total del perro/dispositivo.
- Admin: invitar/revocar usuarios, ajustar duración de invitaciones temporales, transferencias.

### Family
- **Control completo del dispositivo y funciones del perro** (igual que Owner en “funcionalidad”), excepto:
  - No puede expulsar al Owner.
  - No puede transferir propiedad.
  - No puede cambiar configuración de cuenta/billing.
  - Social: restringido si aplica (no moderación/administración).

### Temporal (invitación con caducidad)
- Acceso a:
  - Funciones de “encontrar”: Find Nearby, LED Find, Ping.
  - Funciones del perro: salud, paseos, rutinas (según app).
- Sin acceso a:
  - Social.
  - Administración de cuenta.
  - Transferencias / revocaciones.

### Caducidad
- Default: **24h**.
- El Owner elige duración por invitación (presets sugeridos: 2h / 24h / 7d).

---

## Anti-abuso y seguridad
### Reglas mínimas
- Requiere sesión válida + permisos del rol.
- BLE con enlace cifrado (bonding/whitelist).
- Comandos “encontrar” solo cuando el móvil está realmente cerca:
  - RSSI alto sostenido (ej. N lecturas consecutivas por encima de umbral).

### Rate limits (default v1 — “Balanceado”)
- **Ping**: hasta **6/min**.
- **LED Find**: 60 s por activación, cooldown 20 s.
- Sesión Find: 5 min máx (extensible 1 vez por el usuario si batería lo permite).

### Privacidad
- Evitar identificadores BLE estáticos rastreables (usar direcciones aleatorias/resolubles).

---

## LED Find: política por batería (Plan 2)
- **>20%**: LED Find normal.
- **10–20%**: brillo reducido + activación limitada.
- **<10%**: bloquear LED Find; permitir solo Ping micro-flash y lectura.

### PING (micro-destello)
- Duración recomendada: 100–300 ms.
- No entra en “modo Find”; es solo confirmación rápida.

---

## Emparejamiento / Vinculación / Transferencia
### Principio
Si el dispositivo ya está vinculado a una cuenta/perro, un tercero con la app **no puede controlarlo** sin credenciales y autorización.

### Método principal (sin botón): “Dock magnético”
- Para permitir **nuevo bonding/transferencia**, el dispositivo exige estado “cargando” (detecta carga).
- El Owner inicia proceso en app → backend emite token de 1 uso (expira) → app lo entrega por BLE → el tracker valida token y completa bonding.

### Fallback: “Patrón de luces”
- El tracker muestra un patrón/código por LED.
- El Owner lo confirma en app dentro de una ventana corta.

---

## QA / Tests mínimos (para cerrar números reales)
1) **Latencia de detección** en interior/exterior con Standby por ventanas (periodos 3–4–6–8 s).
2) **Consumo promedio**: Standby ventanas vs Find Activo (con y sin Coded PHY).
3) **RSSI estabilidad**: porcentaje de “falsas subidas/bajadas” en interior.
4) **Batería/LED**: impacto de 1 min LED Find y límites por batería.
5) **Abuso**: rate limit, intentos sin permisos, intentos con RSSI bajo.

---

## Decision Log
- **DL-001**: Find Nearby v1 será hot/cold RSSI (sin flecha).
- **DL-002**: Coded PHY solo en Find Activo.
- **DL-003**: BLE Standby por ventanas con objetivo ≤5 s.
- **DL-004**: Family con control completo funcional (sin administración/propiedad).
- **DL-005**: Temporal con acceso completo a funciones del perro + “encontrar”, sin social/cuenta.
- **DL-006**: Pairing sin botón físico: cargando como prueba principal + patrón LED como fallback.
- **DL-007**: LED Find por batería Plan 2 + Ping con micro-destello.

---

## Risk Register
- **RR-001 (Consumo BLE real)**: Ventanas demasiado frecuentes suben consumo.
  - Mitigación: medir mA promedio y ajustar periodo/duración.
- **RR-002 (RSSI interior inestable)**: UX frustrante.
  - Mitigación: filtro mediana/EMA, tendencia, copy honesto.
- **RR-003 (Secuestro de pairing)**: acceso no autorizado.
  - Mitigación: token 1 uso + prueba física (carga/patrón LED) + RSSI alto sostenido.

