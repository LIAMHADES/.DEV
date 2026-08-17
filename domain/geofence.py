"""
Geofence evaluation logic.

Supports polygon geofences with point-in-polygon check.
Implements:
- 2-reading confirmation before triggering EXIT event
- Cooldown between repeated alerts
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
from shapely.geometry import Point, Polygon, shape
from dataclasses import dataclass


@dataclass
class GeofenceState:
    """Tracks the state of a dog relative to a geofence."""
    dog_id: int
    geofence_id: int
    consecutive_out: int = 0
    last_alert_time: Optional[datetime] = None
    current_status: str = "IN_ZONE"  # IN_ZONE, OUT_ZONE, UNKNOWN


@dataclass
class GeofenceCheckResult:
    is_inside: bool
    distance_to_boundary_m: Optional[float] = None
    should_trigger_exit: bool = False
    should_trigger_enter: bool = False


def check_point_in_polygon(
    lat: float,
    lon: float,
    polygon_geojson: dict,
    tolerance_m: float = 5.0
) -> GeofenceCheckResult:
    """
    Check if a point is inside a GeoJSON polygon.
    
    Args:
        lat: Latitude of the point.
        lon: Longitude of the point.
        polygon_geojson: GeoJSON polygon definition.
        tolerance_m: Tolerance in meters (not used in basic check, for future enhancement).
        
    Returns:
        GeofenceCheckResult with is_inside status.
    """
    try:
        point = Point(lon, lat)  # Note: GeoJSON uses lon, lat order
        polygon = shape(polygon_geojson)
        
        is_inside = polygon.contains(point)
        
        return GeofenceCheckResult(is_inside=is_inside)
    except Exception as e:
        # If geometry is invalid, assume inside to avoid false alerts
        return GeofenceCheckResult(is_inside=True)


def check_point_in_circle(
    lat: float,
    lon: float,
    center_lat: float,
    center_lon: float,
    radius_m: float
) -> GeofenceCheckResult:
    """
    Check if a point is inside a circular geofence.
    
    Uses Haversine formula for distance calculation.
    """
    from math import radians, cos, sin, sqrt, atan2
    
    R = 6371000  # Earth's radius in meters
    
    lat1, lon1, lat2, lon2 = map(radians, [lat, lon, center_lat, center_lon])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    distance = R * c
    
    is_inside = distance <= radius_m
    
    return GeofenceCheckResult(
        is_inside=is_inside,
        distance_to_boundary_m=abs(distance - radius_m) if not is_inside else 0
    )


def evaluate_geofence_transition(
    current_check: GeofenceCheckResult,
    state: GeofenceState,
    confirm_readings: int = 2,
    cooldown_minutes: int = 5
) -> Tuple[GeofenceState, bool, bool]:
    """
    Evaluate if a geofence transition should trigger an event.
    
    Implements:
    - N consecutive readings outside before triggering EXIT
    - Cooldown period between repeated alerts
    
    Args:
        current_check: Result of the current location check.
        state: Current geofence state for this dog.
        confirm_readings: Number of consecutive OUT readings needed.
        cooldown_minutes: Minutes to wait before re-alerting.
        
    Returns:
        Tuple of (updated_state, should_exit_alert, should_enter_alert)
    """
    now = datetime.utcnow()
    should_exit = False
    should_enter = False
    
    if current_check.is_inside:
        # Point is inside
        if state.current_status == "OUT_ZONE":
            # Transition from OUT to IN
            should_enter = True
            state.current_status = "IN_ZONE"
        state.consecutive_out = 0
    else:
        # Point is outside
        state.consecutive_out += 1
        
        if state.consecutive_out >= confirm_readings:
            # Confirmed outside
            if state.current_status == "IN_ZONE":
                # Check cooldown
                if state.last_alert_time is None or \
                   (now - state.last_alert_time) > timedelta(minutes=cooldown_minutes):
                    should_exit = True
                    state.last_alert_time = now
                
                state.current_status = "OUT_ZONE"
    
    return state, should_exit, should_enter
