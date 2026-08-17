"""
ARES GPS Backend - FastAPI Application Entry Point
"""
from config import settings
from models import Device, Dog, DogMode, Event, EventType, Alert
from database import SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routes import auth, dogs, devices, dev, iot

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ARES GPS API",
    description="Backend for ARES Dog GPS Tracking and Health Application",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(dogs.router)
app.include_router(devices.router)
app.include_router(iot.router)
app.include_router(dev.router)


# --- Watchdog Background Task ---

async def watchdog_task():
    """
    Periodically checks for devices that haven't sent coordinates in the specified time.
    """
    while True:
        db: Session = SessionLocal()
        try:
            now = datetime.utcnow()

            # Find all active devices
            devices = db.query(Device).filter(Device.status == "active").all()

            for device in devices:
                dog = device.dog
                if not dog:
                    continue

                # Determine limit based on mode
                limit_minutes = settings.WATCHDOG_WALKING_MINUTES if dog.mode == DogMode.WALKING else settings.WATCHDOG_REST_MINUTES

                last_seen = device.last_seen_at or device.created_at

                if (now - last_seen) > timedelta(minutes=limit_minutes):
                    # Device is silent. Check if we already created a silent event recently
                    last_event = db.query(Event).filter(
                        Event.dog_id == dog.id,
                        Event.type == EventType.SILENT_DEVICE
                    ).order_by(Event.ts.desc()).first()

                    # Alert every 10 minutes if still silent
                    if not last_event or (now - last_event.ts) > timedelta(minutes=10):
                        print(
                            f"WATCHDOG: Device {device.msisdn} is silent for {limit_minutes} minutes. Creating event.")
                        event = Event(
                            dog_id=dog.id,
                            type=EventType.SILENT_DEVICE,
                            payload_json={"last_seen": last_seen.isoformat()}
                        )
                        db.add(event)
                        db.flush()

                        alert = Alert(event_id=event.id, channel="in_app")
                        db.add(alert)
                        db.commit()

        except Exception as e:
            print(f"WATCHDOG ERROR: {e}")
        finally:
            db.close()

        await asyncio.sleep(60)  # Check every minute


@app.on_event("startup")
async def startup_event():
    # Start the watchdog task in the background
    if settings.WATCHDOG_ENABLED:
        asyncio.create_task(watchdog_task())


@app.get("/")
def root():
    return {"message": "ARES GPS API is running", "version": "0.1.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
