"""
ARES v4.0 Global Database Synchronizer (v2.1)
Ensures ALL tables in the database match the v4.0 SQLAlchemy models.
Covers Locations, Geofences, States, Devices, and Dogs.
"""
import sys
import os
from sqlalchemy import text

# Add the app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

try:
    from database import engine, SessionLocal
except ImportError as e:
    print(f"Error importing database module: {e}")
    sys.exit(1)


def sync_db():
    db = SessionLocal()
    print("Connecting to database for GLOBAL synchronization...")

    try:
        # --- 1. Enums ---
        print("Checking Enums...")
        enums = [
            ("activitymode", "('REST', 'WALK', 'JOG', 'RUN', 'VEHICLE')"),
            ("dogmode", "('walking', 'rest')"),
            ("eventtype", "('geofence_exit', 'geofence_enter', 'low_battery', 'no_fix', 'silent_device')"),
            ("alertstatus", "('pending', 'delivered', 'failed')"),
            ("geofencestatestatus", "('unknown', 'inside', 'outside')"),
            ("commandstatus",
             "('pending', 'dispatched', 'sent', 'failed', 'expired', 'acked')")
        ]
        for enum_name, enum_values in enums:
            try:
                db.execute(
                    text(f"CREATE TYPE {enum_name} AS ENUM {enum_values};"))
                db.commit()
                # print(f"  Created Enum '{enum_name}'.")
            except Exception:
                db.rollback()
                # print(f"  Enum '{enum_name}' already exists.")

        # --- 2. Table Column Sync ---
        # Format: (table_name, [(col_name, col_type)])
        tables_to_sync = [
            ("locations", [
                ("battery", "INTEGER"),
                ("battery_mv", "INTEGER"),
                ("battery_capacity_mah", "INTEGER"),
                ("activity_score", "FLOAT"),
                ("temperature", "FLOAT"),
                ("accuracy", "FLOAT"),
                ("horiz_accuracy", "FLOAT"),
                ("satellites", "INTEGER"),
                ("altitude", "FLOAT"),
                ("baro_m", "FLOAT"),
                ("altitude_gain", "FLOAT"),
                ("activity_mode", "activitymode"),
                ("speed_kmh", "FLOAT"),
                ("heading_deg", "FLOAT"),
                ("fix_type", "VARCHAR(20)"),
                ("fix_mode", "VARCHAR(10)"),
                ("source", "VARCHAR(50)"),
                ("cell_id", "VARCHAR(100)"),
                ("wifi_aps", "JSON"),
                ("is_predicted", "BOOLEAN DEFAULT FALSE"),
                ("motion_state", "VARCHAR(20)")
            ]),
            ("geofences", [
                ("tolerance_m", "FLOAT DEFAULT 5.0"),
                ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                ("polygon_geojson", "JSON"),
                ("center_lat", "FLOAT"),
                ("center_lon", "FLOAT"),
                ("radius_m", "FLOAT"),
                ("active", "BOOLEAN DEFAULT TRUE")
            ]),
            ("geofence_states", [
                ("state", "geofencestatestatus DEFAULT 'unknown'"),
                ("consecutive_out", "INTEGER DEFAULT 0"),
                ("consecutive_in", "INTEGER DEFAULT 0"),
                ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                ("last_location_ts", "TIMESTAMP"),
                ("last_exit_alert_at", "TIMESTAMP"),
                ("last_enter_alert_at", "TIMESTAMP")
            ]),
            ("devices", [
                ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                ("device_key_hash", "VARCHAR(255)"),
                ("imei", "VARCHAR(20)")
            ]),
            ("dogs", [
                ("weight_kg", "FLOAT"),
                ("height_cm", "FLOAT"),
                ("age_years", "FLOAT"),
                ("sex", "VARCHAR(10)"),
                ("neutered", "BOOLEAN DEFAULT FALSE"),
                ("mode", "dogmode DEFAULT 'rest'")
            ])
        ]

        print("\nSyncing Table Schemas...")
        for table_name, columns in tables_to_sync:
            print(f"Table '{table_name}':")
            for col_name, col_type in columns:
                try:
                    db.execute(text(
                        f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
                    db.commit()
                    print(f"  - Column '{col_name}' verified/added.")
                except Exception as e:
                    db.rollback()
                    print(f"  - ❌ Failed column '{col_name}': {e}")

        print("\n✅ Global database synchronization complete.")

    except Exception as e:
        print(f"❌ Critical error during sync: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    sync_db()
