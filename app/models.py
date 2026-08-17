from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Enum,
    PrimaryKeyConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
import enum

from database import Base


class DogMode(str, enum.Enum):
    WALKING = "walking"
    REST = "rest"


class ActivityMode(str, enum.Enum):
    REST = "REST"
    WALK = "WALK"
    JOG = "JOG"
    RUN = "RUN"
    VEHICLE = "VEHICLE"


class EventType(str, enum.Enum):
    GEOFENCE_EXIT = "geofence_exit"
    GEOFENCE_ENTER = "geofence_enter"
    LOW_BATTERY = "low_battery"
    NO_FIX = "no_fix"
    SILENT_DEVICE = "silent_device"


class AlertStatus(str, enum.Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"


class GeofenceStateStatus(str, enum.Enum):
    UNKNOWN = "unknown"
    INSIDE = "inside"
    OUTSIDE = "outside"


class CommandStatus(str, enum.Enum):
    PENDING = "pending"
    DISPATCHED = "dispatched"
    SENT = "sent"
    FAILED = "failed"
    EXPIRED = "expired"
    ACKED = "acked"


# --- Users ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    dogs = relationship("Dog", back_populates="owner")


# --- Breeds ---
class Breed(Base):
    __tablename__ = "breeds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    size_category = Column(String(20))  # Toy, Small, Medium, Large, Giant
    avg_weight_kg = Column(Float)
    avg_height_cm = Column(Float)
    activity_multiplier = Column(Float, default=1.0)
    imc_min = Column(Float)
    imc_max = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    primary_dogs = relationship(
        "Dog", foreign_keys="Dog.breed_primary_id", back_populates="primary_breed_rel")
    secondary_dogs = relationship(
        "Dog", foreign_keys="Dog.breed_secondary_id", back_populates="secondary_breed_rel")


# --- Dogs ---
class Dog(Base):
    __tablename__ = "dogs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    age_years = Column(Float, nullable=True)
    sex = Column(String(10), nullable=True)
    neutered = Column(Boolean, default=False)

    breed_primary_id = Column(Integer, ForeignKey("breeds.id"), nullable=True)
    breed_secondary_id = Column(
        Integer, ForeignKey("breeds.id"), nullable=True)

    # Keep strings for fallback or simple display
    breed_primary = Column(String(100), default="Mestizo")
    breed_secondary = Column(String(100), nullable=True)

    mode = Column(Enum(DogMode), default=DogMode.REST)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="dogs")
    primary_breed_rel = relationship(
        "Breed", foreign_keys=[breed_primary_id], back_populates="primary_dogs")
    secondary_breed_rel = relationship(
        "Breed", foreign_keys=[breed_secondary_id], back_populates="secondary_dogs")

    devices = relationship("Device", back_populates="dog")
    locations = relationship("Location", back_populates="dog")
    geofences = relationship("Geofence", back_populates="dog")
    geofence_states = relationship("GeofenceState", back_populates="dog")
    events = relationship("Event", back_populates="dog")
    activity_daily = relationship("ActivityDaily", back_populates="dog")


# --- Devices (Trackers) ---
class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    dog_id = Column(Integer, ForeignKey("dogs.id"), nullable=False)
    msisdn = Column(String(20), unique=True, index=True,
                    nullable=False)  # Tracker phone number
    imei = Column(String(20), nullable=True)
    alias = Column(String(50), nullable=True)
    status = Column(String(20), default="active")
    last_seen_at = Column(DateTime, nullable=True)
    device_key_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    dog = relationship("Dog", back_populates="devices")
    locations = relationship("Location", back_populates="device")
    commands = relationship("DeviceCommand", back_populates="device")


# --- Locations ---
class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    dog_id = Column(Integer, ForeignKey("dogs.id"), nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    ts = Column(DateTime, nullable=False)
    battery = Column(Integer, nullable=True)  # Percentage
    battery_mv = Column(Integer, nullable=True)  # Millivolts
    battery_capacity_mah = Column(Integer, nullable=True)  # 850, 1200, 2800
    activity_score = Column(Float, nullable=True)  # IMU data (BMI270)
    temperature = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    horiz_accuracy = Column(Float, nullable=True)
    satellites = Column(Integer, nullable=True)
    altitude = Column(Float, nullable=True)     # Metros sobre el nivel del mar
    baro_m = Column(Float, nullable=True)
    # Elevación acumulada en la sesión
    altitude_gain = Column(Float, default=0.0)
    activity_mode = Column(Enum(ActivityMode), nullable=True)
    speed_kmh = Column(Float, nullable=True)
    heading_deg = Column(Float, nullable=True)
    fix_type = Column(String(20), nullable=True)  # GNSS, WiFi, CellID
    fix_mode = Column(String(10), nullable=True)
    source = Column(String(50), default="gps")
    cell_id = Column(String(100), nullable=True)
    wifi_aps = Column(JSON, nullable=True)  # List of {bssid, rssi}
    is_predicted = Column(Boolean, default=False)  # True if Kalman prediction
    steps_count = Column(Integer, default=0)    # Steps since last packet
    cadence = Column(Integer, default=0)        # steps/min
    gnss_confidence = Column(Integer, default=100)  # 0-100 score
    signal_rssi = Column(Integer, nullable=True)  # LTE Signal
    created_at = Column(DateTime, default=datetime.utcnow)

    device = relationship("Device", back_populates="locations")
    dog = relationship("Dog", back_populates="locations")

    __table_args__ = (
        UniqueConstraint("dog_id", "ts", "lat", "lon",
                         name="uq_location_point"),
        Index("ix_location_dog_ts", "dog_id", "ts"),
    )


# --- Geofences ---
class Geofence(Base):
    __tablename__ = "geofences"

    id = Column(Integer, primary_key=True, index=True)
    dog_id = Column(Integer, ForeignKey("dogs.id"), nullable=False)
    name = Column(String(100), default="Home")
    type = Column(String(20), default="polygon")
    polygon_geojson = Column(JSON, nullable=True)
    center_lat = Column(Float, nullable=True)
    center_lon = Column(Float, nullable=True)
    radius_m = Column(Float, nullable=True)
    tolerance_m = Column(Float, default=5.0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    dog = relationship("Dog", back_populates="geofences")
    states = relationship("GeofenceState", back_populates="geofence")


# --- Geofence State (Persistent) ---
class GeofenceState(Base):
    __tablename__ = "geofence_states"

    dog_id = Column(Integer, ForeignKey("dogs.id"), nullable=False)
    geofence_id = Column(Integer, ForeignKey("geofences.id"), nullable=False)
    state = Column(Enum(GeofenceStateStatus),
                   default=GeofenceStateStatus.UNKNOWN, nullable=False)
    consecutive_out = Column(Integer, default=0, nullable=False)
    consecutive_in = Column(Integer, default=0, nullable=False)
    last_location_ts = Column(DateTime, nullable=True)
    last_exit_alert_at = Column(DateTime, nullable=True)
    last_enter_alert_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    dog = relationship("Dog", back_populates="geofence_states")
    geofence = relationship("Geofence", back_populates="states")

    __table_args__ = (
        PrimaryKeyConstraint("dog_id", "geofence_id",
                             name="pk_geofence_states"),
    )


# --- Events ---
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    dog_id = Column(Integer, ForeignKey("dogs.id"), nullable=False)
    type = Column(Enum(EventType), nullable=False)
    ts = Column(DateTime, default=datetime.utcnow)
    payload_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    dog = relationship("Dog", back_populates="events")
    alerts = relationship("Alert", back_populates="event")


# --- Alerts ---
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    channel = Column(String(20), default="in_app")
    status = Column(Enum(AlertStatus), default=AlertStatus.PENDING)
    delivered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="alerts")


# --- Activity Daily ---
class ActivityDaily(Base):
    __tablename__ = "activity_daily"

    id = Column(Integer, primary_key=True, index=True)
    dog_id = Column(Integer, ForeignKey("dogs.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    distance_km = Column(Float, default=0.0)
    duration_min = Column(Float, default=0.0)
    steps_est = Column(Integer, default=0)
    cadence_max = Column(Integer, default=0)
    energy_score_avg = Column(Float, default=0.0)
    kcal_burned = Column(Float, default=0.0)
    kcal_target = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    dog = relationship("Dog", back_populates="activity_daily")


# --- Device Commands ---
class DeviceCommand(Base):
    __tablename__ = "device_commands"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    command = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=True)
    status = Column(Enum(CommandStatus),
                    default=CommandStatus.PENDING, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    last_attempt_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    dispatched_at = Column(DateTime, nullable=True)
    dispatched_by = Column(String(50), nullable=True)

    device = relationship("Device", back_populates="commands")

    __table_args__ = (
        Index(
            "ix_device_command_device_status_exp_created",
            "device_id", "status", "expires_at", "created_at"
        ),
    )
