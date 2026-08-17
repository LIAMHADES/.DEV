# SPEC_01: Identidad, Onboarding y Seguridad (ARES v4.0)

**Objetivo**: Definir el ciclo de vida del dispositivo, desde que sale de la caja hasta que se gestiona por múltiples usuarios.

## 1. Onboarding "Sin Fricción" (Plug & Play)

### 1.1. Flujo de Vinculación

1.  **QR Code**: Cada dispositivo tiene una etiqueta con QR que codifica `https://ares.app/c/{device_id}/{secure_token}`.
    - _Fallback_: Entrada manual de `Serial Number` (visible en carcasa).
2.  **Claim Endpoint**: `POST /v1/devices/claim`.
    - Auth: Requiere usuario logueado en App.
    - Payload: `device_id`, `token`.
    - Logic: Si el dispositivo no tiene `owner_id`, se asigna al usuario. Si ya tiene, error (o solicitud de transferencia).
3.  **Setup Inicial (Wizard 3 pasos)**:
    - **Paso 1**: Asignar nombre e icono/foto.
    - **Paso 2**: Perfil del Perro (Raza, Peso, Edad, Sexo, Esterilizado). _Vital para algoritmos de salud._
    - **Paso 3**: "Encender y agitar". El dispositivo envía primer ping. La App lo detecta y muestra "Conectado".

### 1.2. Gestión de Roles (Familia y Cuidadores)

Los permisos se gestionan a nivel de **Relación Usuario-Dispositivo**.

- **OWNER (Propietario)**:
  - Puede: Todo (Desvincular, Factory Reset, OTA, gestionar usuarios).
  - Recibe: Facturación de suscripción.
- **ADMIN (Familiar/Pareja)**:
  - Puede: Ver mapa, Live Mode, Cambiar Luces, Editar Geofences.
  - No puede: Borrar dispositivo, echar al Owner.
- **VIEWER (Paseador/Cuidador temporal)**:
  - Puede: Ver ubicación, encender luz (si se permite).
  - No puede: Ver historial pasado, editar o configurar.
  - _Feature_: "Acceso temporal" (ej. válido por 24h).

## 2. Diagnóstico y Fiabilidad

### 2.1. Estado Visible en App

Pantalla "Ajustes > Dispositivo > Diagnóstico":

- **Estado de Red**: Online/Offline + Tipo (LTE-M / NB-IoT) + RSSI (Barras).
- **GNSS**: Calidad (HDOP), Satélites, "Age of Fix" (hace cuánto fue la última pos real).
- **Sistema**: Batería %, Versión FW, Uptime.
- **Last Reset Reason**: Código de la última causa de reinicio (PowerOn, Watchdog, Brownout, Panic). _Clave para soporte._

### 2.2. Telemetría de Salud del Dispositivo (Heartbeat)

El dispositivo envía en cada paquete (o periódicamente):

- `uptime_s`: Segundos encendido.
- `reset_reason`: Enum (0:Power, 1:WDT, etc).
- `failed_tx_count`: Contador de envíos fallidos (calidad de red).

## 3. OTA (Actualizaciones) y Seguridad

### 3.1. Proceso OTA Seguro

1.  **Check**: Dispositivo consulta `/v1/iot/ota/check` enviando su `fw_version`.
2.  **Notification**: Si hay update crítico, Backend responde con URL firmada.
3.  **Download**: Dispositivo descarga en partición secundaria (A/B partitioning).
4.  **Verify**: Checksum (SHA256) + Firma digital (recomendado).
5.  **Apply**: Reinicio y swap de partición.
6.  **Rollback**: Si la nueva versión crashea (boot loop), el bootloader vuelve a la partición anterior automáticamente.

### 3.2. Seguridad de Comandos

- Todo comando crítico (Wipe, Unlock, OTA) debe ir firmado o usar un token rotativo (rolling code) si es posible, o confiar en la encriptación de transporte (TLS/DTLS) como mínimo basal.
- Autenticación de dispositivo: Header `X-Device-Key` (HMAC SHA256) en cada request HTTPS.
