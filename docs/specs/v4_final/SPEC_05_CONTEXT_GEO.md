# SPEC_05: Contexto Geoespacial y Reglas (ARES v4.0 Backend)

**Objetivo**: Enriquecer el mapa con información útil para dueños de perros (Parques, Fuentes, Normativa). _Esta funcionalidad es 100% Cloud/App_.

## 1. Puntos de Interés (POI Database)

Base de datos colaborativa o importada (OSM) de lugares relevantes.

### 1.1. Modelo de Datos (`Poi`)

- `type`: park, dog_park (pipican), fountain, vet, shop, beach.
- `attributes`: { "fenced": true, "water": true, "shade": "partial" }.
- `status`: Verified / User_Reported.

### 1.2. API de Descubrimiento

`GET /v1/geo/pois?lat=...&lon=...&radius=5km`

- Devuelve lista para pintar en el mapa de la App.
- Soporte de caché local en el móvil para uso offline.

## 2. Normativa y Reglas de Área (`AreaRule`)

Para informar sobre restricciones legales (Parques Nacionales, Playas en verano).

### 2.1. Modelo (`AreaRule`)

- `geometry`: Polígono (GeoJSON).
- `rule_type`:
  - `leash_required`: Correa obligatoria.
  - `no_dogs`: Prohibido perros.
  - `seasonal`: Restricción por fechas (ej. Playas en verano).
- `message`: Texto corto para notificación ("Playa prohibida de Junio a Septiembre").

### 2.2. Check de Contexto (Backend)

Cuando llega una ubicación (`POST /v1/iot/ingest`):

1.  Servidor verifica (asíncronamente) si punto cae dentro de `AreaRule`.
2.  Si entra en zona restringida -> Generar `Event` / `Alert` (Push: "Has entrado en zona con restricción de correa").

### 2.3. UX en App

- Al tocar un parque en el mapa, mostrar ficha con iconos de normativa.
- Alertas contextuales no intrusivas.
