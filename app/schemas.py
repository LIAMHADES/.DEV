from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# --- Auth ---
class UserCreate(BaseModel):
    phone: str
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    phone: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Dogs ---
class DogCreate(BaseModel):
    name: str
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    age_years: Optional[float] = None
    sex: Optional[str] = None
    neutered: bool = False
    breed_primary: str = "Mestizo"
    breed_secondary: Optional[str] = None


class DogUpdate(BaseModel):
    name: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    age_years: Optional[float] = None
    sex: Optional[str] = None
    neutered: Optional[bool] = None
    breed_primary: Optional[str] = None
    breed_secondary: Optional[str] = None
    mode: Optional[str] = None


class DogResponse(BaseModel):
    id: int
    user_id: int
    name: str
    weight_kg: Optional[float]
    height_cm: Optional[float]
    age_years: Optional[float]
    sex: Optional[str]
    neutered: bool
    breed_primary: str
    breed_secondary: Optional[str]
    mode: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Devices ---
class DeviceCreate(BaseModel):
    dog_id: int
    msisdn: str
    imei: Optional[str] = None
    alias: Optional[str] = None


class DeviceResponse(BaseModel):
    id: int
    dog_id: int
    msisdn: str
    imei: Optional[str]
    alias: Optional[str]
    status: str
    last_seen_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class DeviceKeyResponse(BaseModel):
    device_key: str  # Plain key shown only once


# --- Locations ---
class LocationResponse(BaseModel):
    id: int
    device_id: Optional[int]
    dog_id: int
    lat: float
    lon: float
    ts: datetime
    battery: Optional[int]
    battery_mv: Optional[int]
    battery_capacity_mah: Optional[int]
    activity_score: Optional[float]
    temperature: Optional[float]
    accuracy: Optional[float]
    horiz_accuracy: Optional[float]
    satellites: Optional[int]
    altitude: Optional[float]
    baro_m: Optional[float]
    speed_kmh: Optional[float]
    heading_deg: Optional[float]
    fix_type: Optional[str]
    motion_state: Optional[str]
    fix_mode: Optional[str]
    source: Optional[str]
    quality: Optional[int]
    steps_count: int = 0
    cadence: int = 0
    gnss_confidence: int = 100
    signal_rssi: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- Device Commands ---
class DeviceCommandResponse(BaseModel):
    id: int
    device_id: int
    command: str
    payload: Optional[dict]
    status: str
    attempts: int
    last_attempt_at: Optional[datetime]
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


class DeviceCommandStatusUpdate(BaseModel):
    notes: Optional[str] = None


# --- Geofences ---
class GeofenceCreate(BaseModel):
    name: str = "Home"
    type: str = "polygon"
    polygon_geojson: Optional[dict] = None
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None
    radius_m: Optional[float] = None
    tolerance_m: float = 5.0
    active: bool = True


class GeofenceResponse(BaseModel):
    id: int
    dog_id: int
    name: str
    type: str
    polygon_geojson: Optional[dict]
    center_lat: Optional[float]
    center_lon: Optional[float]
    radius_m: Optional[float]
    tolerance_m: float
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Events & Alerts ---
class EventResponse(BaseModel):
    id: int
    dog_id: int
    type: str
    ts: datetime
    payload_json: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    id: int
    event_id: int
    event_type: Optional[str] = None  # Added for convenience
    channel: str
    status: str
    delivered_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# --- Activity ---
class ActivityDailyResponse(BaseModel):
    id: int
    dog_id: int
    date: datetime
    distance_km: float
    duration_min: float
    steps_est: int
    cadence_max: int = 0
    energy_score_avg: float = 0.0
    kcal_burned: float
    kcal_target: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# --- Simulation ---
class SimulateLocationCreate(BaseModel):
    dog_id: int
    lat: float
    lon: float
    ts: Optional[datetime] = None
    battery: Optional[int] = 100


# --- IoT Professional Ingestion (v2.0) ---
class IotGpsData(BaseModel):
    lat: float
    lon: float
    accuracy: Optional[float] = None
    horiz_accuracy: Optional[float] = None
    satellites: Optional[int] = None
    altitude: Optional[float] = None
    speed_kmh: Optional[float] = None
    heading_deg: Optional[float] = None
    fix_type: Optional[str] = None


class IotTelemetryData(BaseModel):
    battery_mv: Optional[int] = None
    battery_capacity_mah: Optional[int] = None
    temperature: Optional[float] = None
    activity_score: Optional[float] = None
    baro_m: Optional[float] = None


class IotIngestPacket(BaseModel):
    timestamp: datetime  # Or int if we parse unix
    gps: IotGpsData
    telemetry: Optional[IotTelemetryData] = None
    activity_mode: Optional[str] = "REST"  # REST, WALK, JOG, RUN, VEHICLE
    motion_state: Optional[str] = "MOVING"  # MOVING, STATIONARY, CHARGING
    cell_id: Optional[str] = None
    steps_count: Optional[int] = 0
    cadence: Optional[int] = 0
    gnss_confidence: Optional[int] = 100
    lte_rssi: Optional[int] = None
    wifi_aps: Optional[List[dict]] = None
    is_predicted: bool = False


class IotIngestBatch(BaseModel):
    device_id: str  # IMEI or Device Serial
    packets: List[IotIngestPacket]


# --- Mobile App (Fast-First) ---
class DeviceStateResponse(BaseModel):
    id: int
    status: str
    battery_pct: Optional[int] = None
    battery_mv: Optional[int] = None
    last_seen_at: Optional[datetime] = None
    mode: str

    class Config:
        from_attributes = True


class MapPulseResponse(BaseModel):
    dog_id: int
    last_location: Optional[LocationResponse]
    device_state: Optional[DeviceStateResponse]


class TrackViewResponse(BaseModel):
    dog_id: int
    points: List[LocationResponse]
    summary: Optional[dict] = None
