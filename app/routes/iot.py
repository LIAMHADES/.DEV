from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List
import hashlib

from database import get_db
from models import Device
from schemas import IotIngestBatch
from services.location_service import process_location_update

router = APIRouter(prefix="/v1/iot", tags=["IoT"])


def verify_device_key(x_device_key: str = Header(...), db: Session = Depends(get_db)):
    """
    Verify the device key against the stored hash.
    Standardized in Hardening v1.1.
    """
    if not x_device_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Device-Key"
        )

    # We verify later during ingest when we have the device_id/IMEI
    return x_device_key


@router.post("/ingest", status_code=status.HTTP_201_CREATED)
def ingest_iot_data(
    batch: IotIngestBatch,
    x_device_key: str = Depends(verify_device_key),
    db: Session = Depends(get_db)
):
    """
    Professional IoT Ingestion Endpoint (v2.0).
    Receives batches of points directly from hardware (BG96/nRF9160).
    """
    # 1. Find device by IMEI
    device = db.query(Device).filter(Device.imei == batch.device_id).first()
    if not device:
        # Fallback to msisdn if device_id matches that
        device = db.query(Device).filter(
            Device.msisdn == batch.device_id).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not registered"
        )

    # 2. Verify Key Hash
    key_hash = hashlib.sha256(x_device_key.encode()).hexdigest()
    if device.device_key_hash != key_hash:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Device Key"
        )

    # 3. Process Batch
    processed_count = 0
    # SORT packets by timestamp to ensure chronological processing
    sorted_packets = sorted(batch.packets, key=lambda p: p.timestamp)

    for packet in sorted_packets:
        process_location_update(
            db=db,
            dog_id=device.dog_id,
            device_id=device.id,
            lat=packet.gps.lat,
            lon=packet.gps.lon,
            ts=packet.timestamp,
            accuracy=packet.gps.accuracy,
            horiz_accuracy=packet.gps.horiz_accuracy,
            satellites=packet.gps.satellites,
            altitude=packet.gps.altitude,
            baro_m=packet.telemetry.baro_m if packet.telemetry else None,
            speed_kmh=packet.gps.speed_kmh,
            heading_deg=packet.gps.heading_deg,
            fix_type=packet.gps.fix_type,
            battery_mv=packet.telemetry.battery_mv if packet.telemetry else None,
            battery_capacity_mah=packet.telemetry.battery_capacity_mah if packet.telemetry else None,
            temperature=packet.telemetry.temperature if packet.telemetry else None,
            activity_score=packet.telemetry.activity_score if packet.telemetry else None,
            activity_mode=packet.activity_mode,
            motion_state=packet.motion_state,
            cell_id=packet.cell_id,
            wifi_aps=packet.wifi_aps,
            is_predicted=packet.is_predicted,
            source="iot",
            fix_mode="GNSS",
            steps_count=packet.steps_count or 0,
            cadence=packet.cadence or 0,
            gnss_confidence=packet.gnss_confidence or 100,
            signal_rssi=packet.lte_rssi
        )
        processed_count += 1

    db.commit()
    return {"status": "ok", "processed": processed_count}
