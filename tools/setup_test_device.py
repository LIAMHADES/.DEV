"""
Standalone script to setup the ARES v4.0 Test Environment.
Registers a test user, dog, and the simulated device (ARES-SIM-001).
"""
import hashlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add the app directory to path so we can import models/database
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

try:
    from database import Base, engine, SessionLocal
    from models import User, Dog, Device, Breed
except ImportError as e:
    print(f"Error importing app modules: {e}")
    print("Executing from the project root? Try: python tools/setup_test_device.py")
    sys.exit(1)


def setup():
    db = SessionLocal()
    print("Connecting to database...")

    try:
        # 1. Ensure test user exists
        user = db.query(User).filter(User.phone == "555000444").first()
        if not user:
            print("Creating test user...")
            user = User(phone="555000444")
            db.add(user)
            db.flush()

        # 2. Ensure test dog exists
        dog = db.query(Dog).filter(Dog.user_id == user.id,
                                   Dog.name == "Simba").first()
        if not dog:
            print("Creating test dog 'Simba'...")
            dog = Dog(
                user_id=user.id,
                name="Simba",
                weight_kg=25.5,
                height_cm=55.0,
                age_years=3,
                sex="MALE"
            )
            db.add(dog)
            db.flush()

        # 3. Register Simulated Device
        device_id = "ARES-SIM-001"
        device_key = "test-device-key-12345"
        key_hash = hashlib.sha256(device_key.encode()).hexdigest()

        device = db.query(Device).filter(Device.imei == device_id).first()
        if not device:
            print(f"Registering Device {device_id}...")
            device = Device(
                imei=device_id,
                msisdn="+34123456789",
                device_key_hash=key_hash,
                dog_id=dog.id
            )
            db.add(device)
        else:
            print(f"Device {device_id} already registered. Updating key hash.")
            device.device_key_hash = key_hash
            device.dog_id = dog.id

        db.commit()
        print("\n" + "="*40)
        print("SUCCESS: Test Environment Ready")
        print(f"User: {user.phone}")
        print(f"Dog:  {dog.name} (ID: {dog.id})")
        print(f"Device IMEI: {device_id}")
        print(f"Device Key:  {device_key}")
        print("="*40)
        print("\nNow you can run: python tools/simulate_device_v4.py")

    except Exception as e:
        db.rollback()
        print(f"Error during setup: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    setup()
