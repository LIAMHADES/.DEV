# ARES GPS & Health Tracker: Single Source of Truth (SSOT) - v4 (Actualizado)

**Misión general del Proyecto ARES:** Crear el dispositivo de seguimiento y salud para perros más avanzado del mercado, combinando localización de alta precisión, un análisis de actividad y bienestar líder en su categoría, y una experiencia de usuario excepcional.

---

**AVISO IMPORTANTE:** Este documento ahora integra la información histórica relevante de la v3.6 junto con las especificaciones de funcionalidades actuales (v4). Para una visión completa, consulte las secciones "TARGET v3.6 (Referencia Histórica)" y "Funcionalidades Actuales v4".

---

## 🗄️ ARCHIVADO — TARGET v3.6 (Referencia Histórica, NO VIGENTE)
> **AVISO:** todo este bloque es histórico (prototipo v3.6, superado por v4.0). Las cifras de aquí (precisión 0.8m, eSIM soldada desde el inicio, packs 850/1200/2800mAh, coste ~33€ modelo NANO) **NO reflejan el producto actual** y contradicen las cifras vigentes en v4.0 (ver más abajo y `docs/investigacion_tracker_diy/PRODUTO/ACTUAL/`). Se mantiene únicamente por trazabilidad histórica del proyecto — **no citar estas cifras en marketing, ventas ni especificación técnica**. La fuente de verdad actual es:
> - Producto/negocio: `docs/investigacion_tracker_diy/PRODUTO/ACTUAL/01_PRODUCTO_Y_NEGOCIO.md`
> - Técnica: `docs/investigacion_tracker_diy/PRODUTO/ACTUAL/02_ESPECIFICACION_TECNICA.md`
> - Specs funcionales: `docs/specs/v4_final/SPEC_01` a `SPEC_05`

_Esta sección contiene la especificación de producción del prototipo v3.6, ya obsoleta. **No debe modificarse directamente aquí.**_

- ~~Precisión Máxima: 0.8m con sistema GNSS Hybrid (Kalman)~~ → **Vigente v4.0: objetivo <1m, pendiente de validación de campo** (Ignion A101+LNA).
- **Sensor Actividad**: Bosch BMI270 para antifraude y predicción — esto sí se mantiene en v4.0.
- ~~SIM: eSIM soldada para máxima fiabilidad~~ → **Vigente v4.0: Nano-SIM en prototipo, migración a MFF2 soldada solo al escalar producción** (ver `ARES_Documento_SIM_eSIM_v1.0.md`).
- ~~Batería: Packs intercambiables en 2 segundos (850/1200/2800mAh)~~ → **Vigente v4.0: Medium ~2750mAh / Large ~4000mAh** (Nano pospuesto, ver `02_ESPECIFICACION_TECNICA.md` §3.1).
- ~~Coste de Fabricación: Desde ~33€ (Modelo NANO)~~ → **Vigente v4.0: ~64€ (Medium) / ~67€ (Large), todo incluido con celda LiPo** (ver `Hardwear.txt`).

---

_Para detalles completos del hardware v3.6 (histórico, no vigente), ver materia prima en: `docs/investigacion_tracker_diy/PRODUTO/ACTUAL/_materia_prima/Hardwear.txt` (es la materia prima de la que se extrajo el BOM v4.0)._

---

## Funcionalidades Actuales ARES (v4) - para Programación

### **Funcionalidades para el Usuario Final (Control vía App)**

#### 1. **Localización y Seguimiento**
*   **Seguimiento GPS en Tiempo Real (Modo Live):** Ver la posición exacta del perro en un mapa con alta frecuencia de actualización.
*   **Historial de Ubicaciones:** Revisar las rutas y lugares visitados.
*   **Búsqueda de Proximidad (Find My Pet):** Usar Bluetooth LE (y/o Wi-Fi) para localizar al perro en un rango corto (aprox. 50m), con una interfaz de "frío/caliente".
*   **Geovallas (Safe Zones):** Crear zonas seguras y recibir alertas instantáneas si el perro entra o sale.

#### 2. **Salud y Actividad Física**
*   **Monitor de Actividad:** Cuantificar minutos de caminata, carrera, juego y descanso.
*   **Análisis del Sueño:** Registrar duración y calidad del sueño.
*   **Cálculo de Ejercicio:** Estimar distancia recorrida y calorías quemadas.
*   **Índice de Bienestar:** Puntuación que resume la salud y actividad general.

#### 3. **Interacción y Control del Dispositivo**
*   **Control Remoto de Luces LED:** Encender, apagar o cambiar el patrón de las luces del collar.
*   **Gestión de Modos de Energía:** Cambiar entre modos para optimizar la batería (Ahorro, Normal, Live).
*   **Notificaciones Inteligentes:**
    *   Alertas de batería baja.
    *   Alertas de Geovalla.
    *   Alertas de actividad (o inactividad inusual).

#### 4. **Social y Comunidad (Futuro)**
*   **Compartir Paseos:** Opción para compartir la ubicación con amigos.
*   **Rankings de Actividad:** Comparar actividad con otros perros (anónimo).

---

### **Funcionalidades para la Empresa (Plataforma y Dispositivo)**

#### 1. **Comunicaciones y Conectividad**
*   **Canal Principal (WAN):** Usar **LTE-M/NB-IoT** para enviar telemetría a la nube (backend).
*   **Canal Secundario (Local):** Usar **BLE** para la función "Find My Pet" y la configuración inicial. Usar **Wi-Fi** para sniffing de ubicación en modo degradado y para actualizaciones de firmware (OTA).
*   **Store & Forward:** El dispositivo debe ser capaz de almacenar puntos de localización si pierde la conexión y enviarlos en bloque cuando lo recupere.

#### 2. **Gestión de Energía y Modos (Firmware)**
*   **Modos de Tasa GNSS:** El firmware debe ajustar la frecuencia de lectura del GPS según el estado del dispositivo (Reposo, Caminando, Corriendo, Cerca de Geovalla, Modo Perdido).
*   **Deep Sleep:** Implementar un modo de sueño profundo agresivo, despertando solo por movimiento detectado por el **IMU (acelerómetro)**.
*   **Telemetría de Energía:** Enviar constantemente el voltaje (`battery_mv`), porcentaje (`battery_pct`) y temperatura (`temperature_c`) de la batería.

#### 3. **Inteligencia en el Dispositivo (Firmware)**
*   **Detección de Movimiento (IMU):** Clasificar el estado entre `REST`, `WALK`, `JOG`, `RUN`, `VEHICLE` sin depender del GPS.
*   **Anti-Fraude Básico:** Marcar los datos cuando se detecta movimiento en vehículo.
*   **Gestión de GPS Degradado:** Si la señal GPS es mala (pocos satélites, baja precisión), el firmware debe marcar la telemetría como de baja calidad y puede intentar obtener una ubicación aproximada por **Cell ID** o **Wi-Fi sniffing**.

#### 4. **Gestión y Diagnóstico Remoto (Backend y Firmware)**
*   **Actualizaciones de Firmware Over-the-Air (FOTA):** El backend debe poder enviar actualizaciones de firmware a los dispositivos.
*   **Telemetría de Diagnóstico:** El dispositivo debe reportar su versión de firmware (`fw_version`), tiempo encendido (`uptime_s`), y la razón del último reinicio (`last_reset_reason`).
*   **Recepción de Comandos:** El dispositivo debe poder recibir y actuar sobre comandos enviados desde el backend (ej. `SET_LOST_MODE`, `SET_GEOFENCE`).
