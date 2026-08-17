from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import math

from models import (
    Dog,
    Geofence,
    Location,
    Event,
    Alert,
    EventType,
    ActivityDaily,
    GeofenceState,
    GeofenceStateStatus,
)
from domain.geofence import check_point_in_polygon, check_point_in_circle
from domain.health import estimate_kcal_burned
from config import settings


def _get_locked_geofence_state(
    db: Session,
    dog_id: int,
    geofence_id: int
) -> GeofenceState:
    state = db.query(GeofenceState).filter(
        GeofenceState.dog_id == dog_id,
        GeofenceState.geofence_id == geofence_id
    ).with_for_update().first()

    if state:
        return state

    state = GeofenceState(
        dog_id=dog_id,
        geofence_id=geofence_id,
        state=GeofenceStateStatus.UNKNOWN,
        consecutive_out=0,
        consecutive_in=0
    )
    db.add(state)
    try:
        db.flush()
        return state
    except IntegrityError:
        db.rollback()
        return db.query(GeofenceState).filter(
            GeofenceState.dog_id == dog_id,
            GeofenceState.geofence_id == geofence_id
        ).with_for_update().first()


def process_location_update(
    db: Session,
    dog_id: int,
    lat: float,
    lon: float,
    ts: datetime,
    battery: int = None,
    battery_mv: int = None,
    fix_mode: str = "GPS",
    source: str = "gps",
    device_id: int = None,
    accuracy: float = None,
    horiz_accuracy: float = None,
    satellites: int = None,
    activity_score: float = None,
    temperature: float = None,
    altitude: float = None,
    baro_m: float = None,
    activity_mode: str = "REST",
    speed_kmh: float = None,
    heading_deg: float = None,
    fix_type: str = None,
    motion_state: str = None,
    cell_id: str = None,
    wifi_aps: list = None,
    battery_capacity_mah: int = None,
    is_predicted: bool = False,
    steps_count: int = 0,
    cadence: int = 0,
    gnss_confidence: int = 100,
    signal_rssi: int = None
):
    """
    Core pipeline for location updates.
    v3.6: Supports Hybrid Localization (Cell-ID, WiFi) and Power Pack monitoring.
    Calculates distance, cumulative altitude, updates activity, evaluates geofences, and triggers alerts.
    Includes ANTI-FRAUDE logic: Validates if the activity mode matches the speed.
    """
    # 1. Fetch last location for gain calculation
    last_loc = db.query(Location).filter(
        Location.dog_id == dog_id
    ).order_by(Location.ts.desc()).first()

    current_gain = 0.0
    if last_loc and altitude is not None and last_loc.altitude is not None:
        gain = altitude - last_loc.altitude
        if gain > 0:
            current_gain = last_loc.altitude_gain + gain
        else:
            current_gain = last_loc.altitude_gain

    # v4.0 Anti-Fraud Logic: Speed vs Motion
    # If speed > 25km/h AND sensor says STATIONARY -> It's a VEHICLE (Fraud/Transport)
    final_activity_mode = activity_mode
    if speed_kmh and speed_kmh > 25.0 and motion_state == "STATIONARY":
        final_activity_mode = "VEHICLE"

    # 2. Create Location record
    location = Location(
        device_id=device_id,
        dog_id=dog_id,
        lat=lat,
        lon=lon,
        ts=ts,
        battery=battery,
        battery_mv=battery_mv,
        battery_capacity_mah=battery_capacity_mah,
        fix_mode=fix_mode,
        source=source,
        accuracy=accuracy,
        horiz_accuracy=horiz_accuracy,
        satellites=satellites,
        activity_score=activity_score,
        temperature=temperature,
        altitude=altitude,
        baro_m=baro_m,
        altitude_gain=current_gain,
        activity_mode=final_activity_mode,
        speed_kmh=speed_kmh,
        heading_deg=heading_deg,
        fix_type=fix_type,
        motion_state=motion_state,
        cell_id=cell_id,
        wifi_aps=wifi_aps,
        is_predicted=is_predicted,
        steps_count=steps_count,
        cadence=cadence,
        gnss_confidence=gnss_confidence,
        signal_rssi=signal_rssi
    )

    # 3. Distance Calculation
    # Note: For pro IoT, we might want to check the previous location only if accuracy is good.
    last_loc = db.query(Location).filter(
        Location.dog_id == dog_id
    ).order_by(Location.ts.desc()).first()

    distance_delta_km = 0.0
    if last_loc:
        R = 6371.0  # Earth radius in km
        dlat = math.radians(lat - last_loc.lat)
        dlon = math.radians(lon - last_loc.lon)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(last_loc.lat)) * \
            math.cos(math.radians(lat)) * \
            math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance_delta_km = R * c

    db.add(location)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        existing = db.query(Location).filter(
            Location.dog_id == dog_id,
            Location.ts == ts,
            Location.lat == lat,
            Location.lon == lon
        ).first()
        if existing:
            # print("Duplicate point ignored")
            return existing
        raise

    # 3. Activity & Kcal
    today = ts.date()
    dog = db.query(Dog).filter(Dog.id == dog_id).first()

    if dog:
        target_date = datetime.combine(today, datetime.min.time())
        activity = db.query(ActivityDaily).filter(
            ActivityDaily.dog_id == dog.id,
            ActivityDaily.date == target_date
        ).first()

        if not activity:
            activity = ActivityDaily(
                dog_id=dog.id,
                date=target_date,
                distance_km=0.0,
                kcal_burned=0.0
            )
            db.add(activity)

        # Anti-fraud: high speed with stationary IMU => VEHICLE (do not count)
        is_vehicle = False
        if speed_kmh is not None and speed_kmh > 25 and motion_state == "STATIONARY":
            is_vehicle = True
            location.motion_state = "VEHICLE"

        # v4.1 IMU-Driven Activity: Using real steps and cadence
        if not is_vehicle:
            # 1. Update steps (Real from hardware)
            if steps_count > 0:
                activity.steps_est += steps_count

            # 2. Update cadence max
            if cadence > activity.cadence_max:
                activity.cadence_max = cadence

            # 3. Update energy score (rolling average or simple moving average)
            # activity_score in Location represents intensity
            if activity_score is not None:
                # Simple weighted average (1/100 weight for new data)
                activity.energy_score_avg = (
                    activity.energy_score_avg * 0.95) + (activity_score * 0.05)

            # 4. Updates distance and Kcal (standard logic)
            if distance_delta_km > 0.005:  # > 5 meters
                activity.distance_km += distance_delta_km
                activity.kcal_burned += estimate_kcal_burned(
                    dog.weight_kg or 20.0, distance_delta_km)

        # 4. Geofence Evaluation (persistent state)
        # Skip geofence if accuracy is very poor (> 50m) to avoid ghost exits
        effective_accuracy = horiz_accuracy if horiz_accuracy is not None else accuracy
        if effective_accuracy is None or effective_accuracy < 50.0:
            geofence = db.query(Geofence).filter(
                Geofence.dog_id == dog.id,
                Geofence.active == True
            ).first()

            if geofence:
                check_result = None
                if geofence.type == "polygon" and geofence.polygon_geojson:
                    check_result = check_point_in_polygon(
                        lat, lon, geofence.polygon_geojson, geofence.tolerance_m)
                elif geofence.type == "circle" and geofence.center_lat and geofence.center_lon and geofence.radius_m:
                    check_result = check_point_in_circle(
                        lat, lon, geofence.center_lat, geofence.center_lon, geofence.radius_m)

                if check_result is not None:
                    now = datetime.utcnow()
                    state = _get_locked_geofence_state(db, dog.id, geofence.id)

                    if state.last_location_ts and ts <= state.last_location_ts:
                        return location

                    should_exit = False
                    should_enter = False

                    if check_result.is_inside:
                        state.consecutive_in += 1
                        state.consecutive_out = 0
                        if state.state != GeofenceStateStatus.INSIDE and \
                           state.consecutive_in >= settings.GEOFENCE_CONFIRM_READINGS:
                            if state.last_enter_alert_at is None or \
                               (now - state.last_enter_alert_at) > timedelta(
                                   minutes=settings.GEOFENCE_COOLDOWN_MINUTES):
                                should_enter = True
                                state.last_enter_alert_at = now
                            state.state = GeofenceStateStatus.INSIDE
                    else:
                        state.consecutive_out += 1
                        state.consecutive_in = 0
                        if state.state != GeofenceStateStatus.OUTSIDE and \
                           state.consecutive_out >= settings.GEOFENCE_CONFIRM_READINGS:
                            if state.last_exit_alert_at is None or \
                               (now - state.last_exit_alert_at) > timedelta(
                                   minutes=settings.GEOFENCE_COOLDOWN_MINUTES):
                                should_exit = True
                                state.last_exit_alert_at = now
                            state.state = GeofenceStateStatus.OUTSIDE

                    state.last_location_ts = ts
                    state.updated_at = now
                    db.add(state)

                    if should_exit:
                        event = Event(
                            dog_id=dog.id,
                            type=EventType.GEOFENCE_EXIT,
                            payload_json={
                                "lat": lat, "lon": lon, "geofence_id": geofence.id, "accuracy": accuracy}
                        )
                        db.add(event)
                        db.flush()
                        db.add(Alert(event_id=event.id, channel="in_app"))

                    if should_enter:
                        event = Event(
                            dog_id=dog.id,
                            type=EventType.GEOFENCE_ENTER,
                            payload_json={
                                "lat": lat, "lon": lon, "geofence_id": geofence.id, "accuracy": accuracy}
                        )
                        db.add(event)

    # 5. Low Battery Alert (Hybrid: % or Voltage)
    is_low = False
    if battery is not None and battery < 20:
        is_low = True
    elif battery_mv is not None and battery_mv < 3400:  # Typical 3.4V threshold for LiPo
        is_low = True

    if is_low:
        event = Event(dog_id=dog_id, type=EventType.LOW_BATTERY,
                      payload_json={"battery": battery, "battery_mv": battery_mv})
        db.add(event)
        db.flush()
        db.add(Alert(event_id=event.id, channel="in_app"))

    return location
