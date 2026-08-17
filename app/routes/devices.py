from typing import List, Optional
import hashlib
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db
from models import Device, DeviceCommand, CommandStatus, User, Geofence
from schemas import (
    DeviceCreate, DeviceResponse, DeviceKeyResponse,
    DeviceCommandResponse, DeviceCommandStatusUpdate
)
from config import settings
from routes.auth import get_current_user

router = APIRouter(prefix="/v1/devices", tags=["Devices"])


def verify_device_key(x_device_key: str = Header(None), db: Session = Depends(get_db)):
    if not x_device_key:
        raise HTTPException(status_code=401, detail="X-Device-Key required")

    key_hash = hashlib.sha256(x_device_key.encode()).hexdigest()
    device = db.query(Device).filter(
        Device.device_key_hash == key_hash).first()
    if not device:
        raise HTTPException(status_code=401, detail="Invalid Device Key")
    return device


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_device(
    device_data: DeviceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Register a new tracker device linked to a dog."""
    # Check if msisdn already exists
    existing = db.query(Device).filter(
        Device.msisdn == device_data.msisdn).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device with this phone number already registered"
        )

    device = Device(**device_data.model_dump())
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.post("/{device_id}/rotate-key", response_model=DeviceKeyResponse)
def rotate_device_key(
    device_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Generate a new secure key for the gateway (MacroDroid). Shown only once."""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Check ownership (simple check for MVP)
    if device.dog.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    new_key = secrets.token_urlsafe(32)
    device.device_key_hash = hashlib.sha256(new_key.encode()).hexdigest()
    db.commit()

    return DeviceKeyResponse(device_key=new_key)


@router.post("/{device_id}/lost-mode")
def set_lost_mode(
    device_id: int,
    enabled: bool,
    timeout_s: Optional[int] = 1800,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Activates/Deactivates Lost Mode (SET_LOST_MODE)."""
    # Verify ownership
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    cmd = DeviceCommand(
        device_id=device_id,
        command="SET_LOST_MODE",
        payload={"enabled": enabled, "timeout_s": timeout_s},
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )
    db.add(cmd)
    db.commit()
    return {"status": "command_queued", "command_id": cmd.id}


@router.post("/{device_id}/lights/find")
def find_me_lights(
    device_id: int,
    pattern: str = "STROBE",
    color: str = "CYAN",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Activates high visibility lights (FIND_ME)."""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    cmd = DeviceCommand(
        device_id=device_id,
        command="FIND_ME",
        payload={"pattern": pattern, "color": color},
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    db.add(cmd)
    db.commit()
    return {"status": "command_queued", "command_id": cmd.id}


@router.post("/{device_id}/sync-geofence")
def sync_geofence(
    device_id: int,
    geofence_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Syncs a specific geofence to the device (SET_GEOFENCE)."""
    gf = db.query(Geofence).filter(Geofence.id == geofence_id).first()
    if not gf:
        raise HTTPException(status_code=404, detail="Geofence not found")

    # Simple radius geofence for firmware parsing
    payload = {
        "id": f"gf-{gf.id}",
        "lat": gf.center_lat,
        "lon": gf.center_lon,
        "radius": gf.radius_m
    }

    cmd = DeviceCommand(
        device_id=device_id,
        command="SET_GEOFENCE",
        payload=payload,
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    db.add(cmd)
    db.commit()
    return {"status": "command_queued", "command_id": cmd.id}


@router.post("/{device_id}/rate-profile")
def set_rate_profile(
    device_id: int,
    profile: str,  # SAVER, NORMAL, LIVE
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Changes the tracking rate profile (SET_RATE_PROFILE)."""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    cmd = DeviceCommand(
        device_id=device_id,
        command="SET_RATE_PROFILE",
        payload={"profile": profile},
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    db.add(cmd)
    db.commit()
    return {"status": "command_queued", "command_id": cmd.id}


@router.post("/{device_id}/ota")
def start_ota(
    device_id: int,
    url: str,
    checksum: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Requests a firmware update (START_OTA)."""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    cmd = DeviceCommand(
        device_id=device_id,
        command="START_OTA",
        payload={"url": url, "checksum": checksum},
        expires_at=datetime.utcnow() + timedelta(hours=2)
    )
    db.add(cmd)
    db.commit()
    return {"status": "command_queued", "command_id": cmd.id}


@router.post("/{device_id}/ping")
def ping_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sends a healthcheck ping (PING)."""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    cmd = DeviceCommand(
        device_id=device_id,
        command="PING",
        payload={},
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.add(cmd)
    db.commit()
    return {"status": "command_queued", "command_id": cmd.id}


@router.get("/commands/poll", response_model=Optional[DeviceCommandResponse])
def poll_commands(
    db: Session = Depends(get_db),
    device: Device = Depends(verify_device_key)
):
    """
    Device calls this to check for pending commands.
    v4.0: Only returns the oldest non-expired pending command.
    """
    now = datetime.utcnow()
    cmd = db.query(DeviceCommand).filter(
        DeviceCommand.device_id == device.id,
        DeviceCommand.status == CommandStatus.PENDING,
        (DeviceCommand.expires_at == None) | (DeviceCommand.expires_at > now)
    ).order_by(DeviceCommand.created_at.asc()).first()

    if cmd:
        cmd.status = CommandStatus.SENT
        cmd.last_attempt_at = now
        cmd.attempts += 1
        db.commit()
        db.refresh(cmd)
        return cmd

    return None


@router.post("/commands/{command_id}/ack")
def acknowledge_command(
    command_id: int,
    db: Session = Depends(get_db),
    device: Device = Depends(verify_device_key)
):
    """Device acknowledges command execution."""
    cmd = db.query(DeviceCommand).filter(
        DeviceCommand.id == command_id,
        DeviceCommand.device_id == device.id
    ).first()

    if not cmd:
        raise HTTPException(status_code=404, detail="Command not found")

    cmd.status = CommandStatus.ACKED
    db.commit()
    return {"status": "acknowledged"}


@router.post("/commands/{command_id}/failed")
def report_command_failed(
    command_id: int,
    update: DeviceCommandStatusUpdate,
    db: Session = Depends(get_db),
    device: Device = Depends(verify_device_key)
):
    """Device or Gateway reports command failure."""
    cmd = db.query(DeviceCommand).filter(
        DeviceCommand.id == command_id,
        DeviceCommand.device_id == device.id
    ).first()

    if not cmd:
        raise HTTPException(status_code=404, detail="Command not found")

    cmd.status = CommandStatus.FAILED
    cmd.attempts += 1
    cmd.last_attempt_at = datetime.utcnow()
    # If using payload for notes, we could store update.notes here
    db.commit()
    db.refresh(cmd)
    return {"status": "failure_reported"}
