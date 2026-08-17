"""
Dog management routes: CRUD for dogs and geofences.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from models import (
    Dog,
    Geofence,
    Location,
    Event,
    Alert,
    ActivityDaily,
    User,
    Device,
    DeviceCommand,
    CommandStatus,
)
from schemas import (
    DogCreate, DogUpdate, DogResponse,
    GeofenceCreate, GeofenceResponse,
    LocationResponse, EventResponse, AlertResponse, ActivityDailyResponse,
    DeviceCommandResponse, MapPulseResponse, TrackViewResponse, DeviceStateResponse
)
from routes.auth import get_current_user
from config import settings

router = APIRouter(prefix="/v1/dogs", tags=["Dogs"])


def check_dog_ownership(dog_id: int, current_user: User, db: Session) -> Dog:
    dog = db.query(Dog).filter(Dog.id == dog_id,
                               Dog.user_id == current_user.id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this dog's data"
        )
    return dog


@router.get("", response_model=List[DogResponse])
def list_dogs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all dogs belonging to the current user."""
    return db.query(Dog).filter(Dog.user_id == current_user.id).all()


@router.post("", response_model=DogResponse, status_code=status.HTTP_201_CREATED)
def create_dog(
    dog_data: DogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new dog profile."""
    dog = Dog(user_id=current_user.id, **dog_data.model_dump())
    db.add(dog)
    db.commit()
    db.refresh(dog)
    return dog


@router.get("/{dog_id}", response_model=DogResponse)
def get_dog(
    dog_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a dog by ID."""
    return check_dog_ownership(dog_id, current_user, db)


@router.patch("/{dog_id}", response_model=DogResponse)
def update_dog(
    dog_id: int,
    dog_data: DogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a dog profile."""
    dog = check_dog_ownership(dog_id, current_user, db)

    update_data = dog_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(dog, key, value)

    db.commit()
    db.refresh(dog)
    return dog

    # --- Locations ---


@router.get("/{dog_id}/last-location", response_model=Optional[LocationResponse])
def get_last_location(
    dog_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the last known location for a dog."""
    check_dog_ownership(dog_id, current_user, db)
    location = db.query(Location).filter(
        Location.dog_id == dog_id
    ).order_by(Location.ts.desc()).first()
    return location


@router.get("/{dog_id}/map/now", response_model=MapPulseResponse)
def get_map_pulse(
    dog_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fast-First 'Pulse' endpoint: Returns current location and device state."""
    check_dog_ownership(dog_id, current_user, db)

    # Get last location
    location = db.query(Location).filter(
        Location.dog_id == dog_id
    ).order_by(Location.ts.desc()).first()

    # Get active device state
    device = db.query(Device).filter(
        Device.dog_id == dog_id,
        Device.status == "active"
    ).first()

    state = None
    if device:
        dog = db.query(Dog).filter(Dog.id == dog_id).first()
        state = DeviceStateResponse(
            id=device.id,
            status=device.status,
            battery_pct=location.battery if location else None,
            battery_mv=location.battery_mv if location else None,
            last_seen_at=device.last_seen_at,
            mode=dog.mode if dog else "ADAPTIVE"
        )

    return MapPulseResponse(
        dog_id=dog_id,
        last_location=location,
        device_state=state
    )


@router.get("/{dog_id}/track/view", response_model=TrackViewResponse)
def get_track_view(
    dog_id: int,
    since: Optional[datetime] = None,
    limit: int = Query(500, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """'Catch-up' endpoint: Returns recent refined route for the map."""
    check_dog_ownership(dog_id, current_user, db)

    query = db.query(Location).filter(Location.dog_id == dog_id)
    if since:
        query = query.filter(Location.ts >= since)
    else:
        # Default to last 24 hours if not specified
        query = query.filter(
            Location.ts >= datetime.utcnow() - timedelta(hours=24))

    points = query.order_by(Location.ts.desc()).limit(limit).all()
    # Reverse to get chronological order for the map
    points.reverse()

    return TrackViewResponse(
        dog_id=dog_id,
        points=points
    )

    # --- Geofences ---


@router.post("/{dog_id}/geofence", response_model=GeofenceResponse, status_code=status.HTTP_201_CREATED)
def create_geofence(
    dog_id: int,
    geofence_data: GeofenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update a geofence for a dog."""
    check_dog_ownership(dog_id, current_user, db)
    # Deactivate existing geofences
    db.query(Geofence).filter(Geofence.dog_id ==
                              dog_id).update({"active": False})

    geofence = Geofence(dog_id=dog_id, **geofence_data.model_dump())
    db.add(geofence)
    db.commit()
    db.refresh(geofence)
    return geofence


@router.get("/{dog_id}/geofence", response_model=Optional[GeofenceResponse])
def get_geofence(
    dog_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active geofence for a dog."""
    check_dog_ownership(dog_id, current_user, db)
    geofence = db.query(Geofence).filter(
        Geofence.dog_id == dog_id,
        Geofence.active == True
    ).first()
    return geofence


# --- Alerts ---
@router.get("/{dog_id}/alerts", response_model=List[AlertResponse])
def get_alerts(
    dog_id: int,
    since: Optional[datetime] = None,
    limit: int = Query(50, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alerts for a dog."""
    check_dog_ownership(dog_id, current_user, db)
    query = db.query(Alert).join(Event).filter(Event.dog_id == dog_id)

    if since:
        query = query.filter(Alert.created_at >= since)

    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    for a in alerts:
        a.event_type = a.event.type
    return alerts


# --- Activity ---
@router.get("/{dog_id}/activity/daily", response_model=Optional[ActivityDailyResponse])
def get_activity_daily(
    dog_id: int,
    date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily activity for a dog."""
    check_dog_ownership(dog_id, current_user, db)
    query = db.query(ActivityDaily).filter(ActivityDaily.dog_id == dog_id)

    if date:
        # Match by date only (ignore time)
        query = query.filter(ActivityDaily.date == date.date())
    else:
        query = query.order_by(ActivityDaily.date.desc())

    return query.first()


# --- Commands ---
@router.post("/{dog_id}/ping", response_model=DeviceCommandResponse, status_code=status.HTTP_201_CREATED)
def ping_dog_device(
    dog_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Queue a 777 ping command for the dog's device."""
    check_dog_ownership(dog_id, current_user, db)

    device = db.query(Device).filter(
        Device.dog_id == dog_id,
        Device.status == "active"
    ).first()
    if not device:
        raise HTTPException(status_code=404, detail="Active device not found")

    # Dedupe/Rate-limit PING
    cooldown = datetime.utcnow() - timedelta(seconds=settings.PING_COOLDOWN_SECONDS)
    existing_ping = db.query(DeviceCommand).filter(
        DeviceCommand.device_id == device.id,
        DeviceCommand.command == "PING",
        DeviceCommand.status == CommandStatus.PENDING,
        DeviceCommand.created_at >= cooldown
    ).first()

    if existing_ping:
        return existing_ping

    expires_at = datetime.utcnow() + \
        timedelta(seconds=settings.PING_TTL_SECONDS)

    cmd = DeviceCommand(
        device_id=device.id,
        command="PING",
        payload={"sms": "777"},
        status=CommandStatus.PENDING,
        expires_at=expires_at
    )
    db.add(cmd)
    db.commit()
    db.refresh(cmd)
    return cmd
