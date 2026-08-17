# ARES — Especificación completa APP (iOS/Android) + Nube  
**Versión:** v0.1 (consolidada)  
**Última actualización:** 2026-01-11  
**Objetivo:** que el editor/desarrollo tenga una referencia única y ejecutable de **qué debe hacer la app**, **qué depende de backend**, **qué datos se intercambian** y **cómo se estructura por tiers**.

---

## 0) Scope y principios (para evitar contradicciones)
- **La app muestra y opera** (UI + lógica ligera).  
- **El backend decide la “verdad oficial”** para rankings, rewards, km válidos, anti‑fraude completo y recomendaciones finales.  
- **El dispositivo manda telemetría**; la app no es “fuente de posición” salvo en **modo degradado** o en asistencias (Find Nearby, onboarding, etc.).  
- **Todo contrato** (campos, enums, topics, endpoints) se define aquí. Sin esto, firmware/app/backend divergen.

---

## 1) Arquitectura APP + Nube (con fases)
### 1.1 App
- **Frontend:** Flutter (iOS/Android)  
- **Mapas online:** Google Maps SDK  
- **Mapas offline:** OSM (recomendación: `flutter_map` + MBTiles; alternativa: descarga de tiles por región)  
- **BLE:** búsqueda cercana + setup local  
- **Streaming real‑time:** MQTT over WebSocket (o WebSocket propio vía backend)

### 1.2 Nube (propuesta híbrida compatible con lo ya definido del tracker)
> La spec del tracker ya asume broker MQTT + backend + PostGIS para histórico geoespacial. Aquí se integra Firebase sin romperlo.

**Broker:** EMQX (Cloud/Managed)  
**Backend core:** FastAPI (ingesta, reglas, alertas, tiers, rewards, anti‑fraude, export)  
**DB core:** PostgreSQL + PostGIS (histórico y queries geo rápidas)  

**Firebase (capas app):**
- **Auth:** Firebase Auth (email/telefono/OAuth)  
- **Push:** FCM  
- **Datos app (opcionales):** Firestore para perfiles, settings, social ligero si se quiere (pero el “core” de tracking/histórico va en PostGIS)

### 1.3 Fases (escalabilidad)
- **Fase 1 (MVP):** EMQX Cloud + backend mínimo + DB core  
- **Fase 2:** Firebase/Firestore para UX y crecimiento (social/ajustes) + escalado de alertas  
- **Fase 3:** AWS IoT Core/IoT Rules si se busca industrializar costos por dispositivo/mes (opcional)

---

# 2) Tiers: Gratis / Plata / Oro (tabla única, sin solapes)
> “TBD” = pendiente de cerrar valores exactos sin bloquear implementación.

## 2.1 Dashboard principal (todas las tiers)
**Widgets base (siempre):**
- Mapa real‑time + indicador de precisión y fuente (`GNSS/CELL/WIFI/MIXED`)
- Estado del tracker: `MOVING/STATIC/CHARGING/LOST_MODE`
- Modo de actividad: `REST/WALK/JOG/RUN/VEHICLE`
- Batería: % + estimación restante (basada en modo GNSS + consumo catálogo)
- Distancia y calorías del día (estimación app; oficial backend)
- Parques cercanos (dog-friendly) + clima/temperatura + recomendación de franja horaria
- Alertas (push) y bandeja de “eventos” (geofence, batería, calor, etc.)

## 2.2 Tabla de features por tier
| Área | Gratis | Plata (4,99€/mes) | Oro (9,99€/mes) |
|---|---|---|---|
| Tracking | Real‑time + histórico **7 días** (local + nube) | Histórico **30 días** | Histórico **1 año** + export veterinario |
| Geofence | 1–2 zonas (TBD) + alertas push | **5 zonas** + alertas avanzadas | 5+ zonas + IA rutas habituales (TBD) |
| Social | Ver amigos (lista) + km semanales | Rutas de amigos + tiempos + mapas | Stats completas + HR estimada (TBD) |
| Ranking | — | **Local** (ciudad/isla) | **Nacional** + por raza |
| Challenges/Grupos | — | Locales semanales + grupos locales | Nacionales mensuales + eventos VIP |
| Dog Fuel (Nutrición) | kcal aprox + escáner básico | kcal exactas + 3 marcas locales + tienda | + proteína óptima + suplementos + histórico dietas |
| Multi‑perro | 1 perro | 1 perro | 2–3 perros (familia) |
| Rewards | cupón 10% por hitos | cupones 15% + rewards ampliados | cupones 20% + beneficios VIP |
| Integraciones | WhatsApp geofence (básico) + offline maps ES | Strava sync básico + afiliados locales | Garmin widget + Home Assistant + GPX completo |

---

# 3) Módulos APP (pantallas, lógica, dependencias)
## 3.1 Autenticación y cuenta
**Pantallas:**
- Login (email/telefono/OAuth)
- Registro
- Recuperación
- Gestión de sesión y dispositivos

**Datos:**
- `user_id`, `email/phone`, `created_at`, `locale`, `subscription_tier`, `privacy_settings`

**Reglas:**
- Sin sesión → no se muestran datos del tracker.
- ACL: un usuario solo ve sus perros/dispositivos y los compartidos con permisos.

---

## 3.2 Onboarding completo (usuario + perro + dispositivo)
### 3.2.1 Flujo UX (tolerante y rápido)
- **Capa 1 (≤30s):** nombre perro → edad → tamaño (selector con iconos)  
- **Capa 2 (precisión):** altura, peso, sexo, raza1 (autocompletar), raza2 (opcional) + ratio (slider 50/50 default)  
- **Capa 3 (opcional):** dieta habitual (pienso/húmeda/mixta/casera)  
- **Feedback inmediato:** si hay discrepancia fuerte → chip “Sugerimos *Mediano* por tus medidas. ¿Cambiar?” (1 click)

### 3.2.2 Entidad `PerroOnboarding` (inputs usuario, no calculados)
Campos mínimos:
- `perro_id (uuid)`
- `usuario_id`
- `nombre_perro`
- `edad_meses` o `fecha_nacimiento`
- `sexo` (M/H/Desconocido)
- `tamano_usuario` (toy/pequeño/mediano/grande/gigante)
- `raza1_id` (opcional)
- `raza2_id` (opcional)
- `mix_ratio_pct` (0–100; default 50 si hay dos razas)
- `altura_cm` (2ª capa)
- `peso_kg` (2ª capa)
- `datos_incongruentes` (bool)

### 3.2.3 Vinculación de dispositivo
**Opciones v1:**
- BLE pairing (QR + BLE)
- WiFi AP para setup (`Roco_Setup_123`) si aplica
- Asociar `device_id` ↔ `perro_id` (1‑a‑1 activo)

**Edge cases:**
- dispositivo ya vinculado → flujo “transferencia” con confirmación y bloqueo
- firmware no responde → diagnóstico + pasos de recuperación

---

## 3.3 Dashboard real‑time (Home)
**Componentes UI:**
- Mapa (posición + precisión)
- Tarjeta estado tracker (modo, batería, señal, fuente posición)
- Tarjeta actividad día (km, kcal, tiempo activo, pace)
- Tarjeta alertas recientes (geofence, batería, calor)
- CTA contextual:
  - “Activar LOST_MODE”
  - “Find Nearby”
  - “Crear geofence”
  - “Subir a Plata/Oro” (según triggers)

**Lógica:**
- La app puede estimar km/kcal en vivo, pero marca “estimado”.
- Backend envía “km válidos” y “kcal oficiales” para rankings/rewards.

---

## 3.4 Mapa + Histórico (Rutas)
**Gratis:** histórico 7 días (local + nube)  
**Plata:** 30 días  
**Oro:** 1 año + export

**Pantallas:**
- Lista sesiones (día/semana/mes)
- Detalle sesión: ruta, km, pace, kcal, flags (GNSS degradado/vehículo)
- Comparativas (Plata/Oro): semana vs semana, percentiles por raza (Oro)

**Datos:**
- `session_id`, `start_ts`, `end_ts`, `distance_m`, `valid_distance_m`, `kcal_est`, `kcal_official`, `quality_flags`

---

## 3.5 Geofence (Valla inteligente)
**Pantallas:**
- Crear/editar geofence (mapa + radio)
- Lista de geofences (máx por tier)
- Histórico salidas/entradas + patrones

**Algoritmo tasa adaptativa (contrato):**
- `<15%` al límite → 2s  
- `15–30%` → 10s  
- `>30%` → 30s  

**Alertas:**
- push siempre
- WhatsApp/Telegram: Plata+ (TBD) o configurable

---

## 3.6 LOST_MODE (Modo perdido)
**Pantallas:**
- Activar (con aviso de consumo)
- Duración (preset 15/30/60 min)
- Cancelar
- Estado visual (LED pattern + badge en app)

**Reglas:**
- Trigger: app → backend → comando a dispositivo
- Timeout o cancelación
- Si batería crítica → backend puede forzar salida

---

## 3.7 Find Nearby (BLE)
**Objetivo:** ayudar a recuperar al perro cerca (≈50–60m).  
**Pantallas:**
- “Buscando…” (RSSI + hot/cold)
- Guía direccional (si se implementa; v1 puede ser solo hot/cold)
- Botón “hacer parpadear LED” (si firmware lo soporta)

---

## 3.8 Social (amigos, feed, privacidad)
**Pantallas:**
- Amigos (lista)
- Perfil (alias, badges, privacidad)
- Compartir con familia (permisos)
- Feed (opcional v1.5)

**Privacidad mínima:**
- ranking por defecto con alias
- ruta exacta solo para familia/propietario
- modo privado: no aparece en rankings/grupos

**Modelo mental:**
- Un usuario tiene N perros
- Un perro puede ser visible por varios usuarios (familia)
- Un dispositivo solo vinculado a 1 perro a la vez

---

## 3.9 Rankings + Challenges + Grupos
**Rankings:**
- Plata: local (ciudad/isla)
- Oro: nacional + por raza

**Challenges:**
- Plata: semanales locales
- Oro: mensuales nacionales

**Grupos:**
- Plata: grupos locales (“Running dogs Palma”)
- Oro: grupos nacionales + eventos VIP (TBD)

**Inputs para ranking:**
- `valid_distance_m` (backend)
- flags anti-fraude (vehículo, GNSS degradado, etc.)

---

## 3.10 Dog Rewards (gamificación)
### 3.10.1 Recompensas automáticas (coste controlado)
- **50km/semana:** cupón 10%  
- **150km/mes:** cupón 15%  
- **350km/mes:** 1 mes Plata gratis  
- **600km/mes:** 2º tracker 20% OFF  

> Los umbrales usan **km válidos backend**. La app solo muestra progreso.

### 3.10.2 Insignias
- 🥉 BRONCE (100km/mes)  
- 🥈 PLATA (250km/mes)  
- 🥇 ORO (500km/mes)  
- 💎 DIAMANTE (1.000km/mes)

**Pantallas:**
- progreso semanal/mensual
- wallet de cupones
- historial de claims

---

## 3.11 Dog Fuel (nutrición IA)
### 3.11.1 Inputs (desde onboarding + logs)
- raza, edad, sexo, peso, esterilización, nivel actividad
- BCS (1–9) y/o IMC si se usa
- objetivos (mantener, bajar, rendimiento)

### 3.11.2 Features por tier
| Función | Gratis | Plata | Oro |
|---|---:|---:|---:|
| Calorías diarias | Aprox | Exactas | + proteína |
| Marcas recomendadas | — | 3 locales | 10 + suplementos |
| % proteína óptima | — | — | Sí |
| Tienda integrada | — | Sí | Sí (mayor comisión) |
| Escáner comida | Cámara básica | IA análisis | Histórico dietas |

### 3.11.3 Log de comida (Registro inteligente)
**Pantallas:**
- capturar foto
- reconocimiento/edición manual
- guardar alimento + cantidad + notas
- histórico y tendencias

**Datos (mínimo):**
- `food_log_id`, `dog_id`, `ts`, `food_name`, `brand`, `portion_g`, `kcal`, `protein_g`, `fat_g`, `carb_g`, `source` (manual/scan)

### 3.11.4 Base de datos de salud (para editor)
Tablas recomendadas (backend/DB):
- `CategoriasTamano`: umbrales por tamaño (incluye riesgo calor/frío)  
- `NivelActividad`: baja/moderada/alta (minutos, distancia aprox)  
- `FactoresEnergeticos`: factores para RER por estado (adulto, esterilizado, cachorro, trabajo intenso…)  
- `NutrientesMinimos`: requerimientos AAFCO por etapa  
- `BCS`: escala 1–9 con % grasa estimado y relación peso ideal  
- `AlimentosToxicos`: lista negra + síntomas + acciones  
- `PerfilPerro`: entidad central  
- históricos: `PesoHistorial`, `ActividadHistorial`, `ComidaHistorial`

> Fórmula RER (referencia veterinaria habitual): `RER = 70 * (peso_kg ^ 0.75)`; MER = RER * factor (tabla FactoresEnergeticos).

---

## 3.12 Salud y bienestar IA (calor, hidratación, fatiga)
**Gratis:**
- índice de calor (temp + humedad) + alertas
- hidratación sugerida (tiempo + intensidad)
- parques óptimos (clima + tipo hierba)

**Plata:**
- “edad biológica” (actividad vs media raza)
- kcal diarias exactas (perfil + actividad)
- marcas cercanas (precio/disponibilidad) (TBD fuente)

**Oro:**
- HR estimado (TBD; depende de modelo/validación)
- fatiga/recuperación 24h
- benchmark por raza (percentiles)

---

## 3.13 Tienda integrada (affiliate + monetización)
**Gratis:** links externos  
**Plata:** tienda integrada (8% comisión) + cupones 15%  
**Oro:** 12% comisión + cupones 20%

**IA de productos:**
- comida según raza/peso/actividad
- suplementos según km/semana
- juguetes según intensidad

---

## 3.14 Export & reporting
- Plata: export básico (TBD)
- Oro: export PDF “veterinario” + GPX completo
- Strava:
  - Plata: KML básico
  - Oro: GPX completo

---

## 3.15 Integraciones externas
**Gratis:**
- mapas offline ES
- WhatsApp alertas geofence (si se activa)

**Plata:**
- Strava sync básico
- afiliados locales (Petco/Mercadona/Kiwoko etc.)

**Oro:**
- Garmin Connect IQ widget (TBD)
- Home Assistant geofence (TBD)
- veterinarios locales PDF (directorio)

---

# 4) Anti‑fraude (contrato app↔backend) — 4 capas
**Objetivo:** rankings justos, rewards fiables.

1) **IMU (device):** patrones aceleración/cadencia  
2) **Velocidad (GNSS):** rango real vs vehículo (>25 km/h sospechoso)  
3) **Teléfono (app):** correlación opcional con Google Fit/HealthKit (Plata/Oro)  
4) **Social (Oro):** confirmación por amigos (TBD; cuidado privacidad)

**Reglas UI (transparencia):**
- “🟢 TROTE 6.2km/h VALIDADO”
- “🚗 Vehículo detectado → 0km ranking”

---

# 5) Notificaciones (push + WhatsApp) y automatizaciones
## 5.1 FCM push (todas)
- geofence
- batería baja
- calor/riesgo
- inmovilidad anómala (Plata+)
- reward conseguido

## 5.2 WhatsApp Business API (tiers y reglas)
- geofence salida (Plata+ recomendado)
- pérdida de señal (Oro/Plata+ TBD)

## 5.3 Flujo 1ª semana (engagement)
- Día 1: parques cercanos + clima
- Día 3: progreso km + cupón (si procede)
- Semana 1: mensaje ranking local → upsell a Plata

---

# 6) Contratos técnicos para desarrollo (lo que el editor necesita)
## 6.1 MQTT topics (mínimo)
- `devices/{device_id}/telemetry` (PUB device)  
- `devices/{device_id}/commands` (SUB device)  
- `users/{user_id}/dogs/{dog_id}/realtime` (PUB backend → app)

## 6.2 Endpoints mínimos (HTTP)
- `POST /api/v1/ingest` (device → backend; punto o batch)  
- `GET /api/v1/devices/{id}/history?from=&to=`  
- `GET /api/v1/dogs/{dog_id}/stats?range=`  
- `POST /api/v1/devices/{id}/lost-mode` (on/off + timeout)  
- `POST /api/v1/geofences` / `PUT /api/v1/geofences/{id}` / `DELETE`  
- `POST /api/v1/rewards/claim`  
- `GET /api/v1/rankings/local` / `GET /api/v1/rankings/national`  
- `POST /api/v1/food/log` / `GET /api/v1/food/log?range=`  
- `POST /api/v1/social/invite` / `POST /api/v1/social/accept`

## 6.3 Payloads clave
### Telemetría (device → backend) — referencia v1
```json
{
  "device_id": "ares-001",
  "seq_id": 123456,
  "ts": "2026-01-11T12:34:56Z",
  "position": {
    "lat": 40.4168,
    "lon": -3.7038,
    "accuracy": 2.1,
    "satellites": 18,
    "speed": 3.2,
    "source": "GNSS",
    "gnss_rate_s": 2
  },
  "state": {
    "status": "MOVING",
    "activity_mode": "RUN",
    "activity_score": 84,
    "gnss_rate_s": 2
  },
  "power": {
    "battery_mv": 3920,
    "battery_pct": 76,
    "temperature_c": 31.4
  },
  "integrity": { "fw_version": "0.1.0" }
}
```

### Comando LOST_MODE (backend → device)
```json
{
  "cmd": "SET_LOST_MODE",
  "enabled": true,
  "timeout_s": 1800,
  "reason": "user_request",
  "ts": "2026-01-11T12:40:00Z"
}
```

### Evento alerta (backend → app)
```json
{
  "type": "GEOFENCE_EXIT",
  "device_id": "ares-001",
  "dog_id": "dog-123",
  "severity": "HIGH",
  "ts": "2026-01-11T12:41:10Z",
  "meta": { "geofence_id": "gf-1", "distance_m": 42 }
}
```

---

# 7) Data model mínimo (para implementación)
## 7.1 Entidades core
- `User`
- `DogProfile`
- `Device`
- `DeviceBinding` (histórico vínculo device↔dog)
- `TelemetryPoint` (PostGIS)
- `Session` (agregado)
- `Geofence`
- `AlertEvent`
- `Subscription`
- `RewardRule`
- `RewardClaim`
- `Coupon`
- `Friendship`
- `Group`
- `Challenge`
- `FoodLog`
- `WeightLog`
- `BCSLog`

## 7.2 Campos mínimos recomendados (resumen)
**DogProfile:** raza(s), edad, sexo, peso, esterilización, tamaño, activity_level, objetivos, privacy  
**Session:** start/end, distancia estimada, distancia válida, kcal estimadas/oficiales, flags, source mix  
**RewardClaim:** regla, periodo, km válidos, estado (pending/approved/issued), cupón/código

---

# 8) Requisitos no funcionales (imprescindibles)
- **Offline:** histórico 7 días local (Gratis), con sync posterior  
- **Rendimiento:** mapa fluido con throttling (no renderizar cada punto si llega a 2s)  
- **Batería móvil:** MQTT solo si pantalla activa; en background usar push + refresh puntual  
- **Privacidad:** controles de visibilidad; no exponer ubicación exacta a terceros  
- **Multi‑idioma:** ES/EN/PT/FR/DE/IT (auto‑detect; strings versionadas)  
- **Analytics:** eventos de funnel (onboarding, activación, upsell, churn)  
- **Observabilidad:** crash reporting + logs de red (Sentry/Firebase Crashlytics)

---

# 9) Decisiones pendientes (bloquean “cerrado 100%”)
1) **Qué parte va en Firebase vs backend core** (recomendación: Auth+Push en Firebase; tracking/histórico/anti‑fraude en backend+PostGIS)  
2) **HR estimado**: entra v1 o es fase 2 (validez médica)  
3) **WhatsApp**: tiers y límites (costes)  
4) **Integraciones**: Garmin/Home Assistant (definir alcance real v1.5)

---

## 10) Entregable siguiente (para ejecutar sin dudas)
1) **Checklist implementable** (APP/BE) con IDs: `APP-xxx`, `BE-xxx`, asociado a tier y a pantallas.  
2) **OpenAPI** (FastAPI) + **ACL MQTT** (topics por usuario/dispositivo) + esquema JSON versionado.
