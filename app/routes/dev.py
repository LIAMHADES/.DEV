from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import SimulateLocationCreate, LocationResponse
from config import settings
from routes.auth import get_current_user
from routes.dogs import check_dog_ownership
from services.location_service import process_location_update

router = APIRouter(prefix="/v1/dev", tags=["Development"])


@router.post("/simulate/location", response_model=LocationResponse)
def simulate_location(
    data: SimulateLocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Simulate a GPS location update.
    Only works if DEV_MODE=True in settings.
    Requires JWT authentication and dog ownership.
    """
    if not settings.DEV_MODE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Simulation endpoints are disabled (DEV_MODE=False)"
        )

    # 1. Check ownership
    check_dog_ownership(data.dog_id, current_user, db)

    # 2. Process location update as simulation
    location = process_location_update(
        db=db,
        dog_id=data.dog_id,
        lat=data.lat,
        lon=data.lon,
        ts=data.ts or datetime.utcnow(),
        battery=data.battery,
        fix_mode="SIM",
        source="simulation"
    )

    db.commit()
    return location
