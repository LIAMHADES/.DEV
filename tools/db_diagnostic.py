"""
Diagnostic script to check for missing columns in the 'locations' table.
Compares the actual DB columns with those expected by the SQLAlchemy model.
"""
import sys
import os
from sqlalchemy import inspect

# Add the app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

try:
    from database import engine, SessionLocal
    from models import Location
except ImportError as e:
    print(f"Error importing app modules: {e}")
    sys.exit(1)


def check_schema():
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('locations')]

    print("=== Database Diagnostic ===")
    print(f"Current columns in 'locations':\n{columns}\n")

    expected_columns = [
        'id', 'device_id', 'dog_id', 'lat', 'lon', 'ts', 'battery',
        'battery_mv', 'battery_capacity_mah', 'activity_score', 'temperature',
        'accuracy', 'horiz_accuracy', 'satellites', 'altitude', 'baro_m',
        'altitude_gain', 'activity_mode', 'speed_kmh', 'heading_deg',
        'fix_type', 'fix_mode', 'source', 'cell_id', 'wifi_aps',
        'is_predicted', 'motion_state', 'created_at'
    ]

    missing = [col for col in expected_columns if col not in columns]

    if not missing:
        print("✅ SUCCESS: All expected columns are present.")
    else:
        print(f"❌ ERROR: Missing columns: {missing}")
        print("\nSQL to fix:")
        for col in missing:
            # We need to match the type from models.py
            if col in ['battery_mv', 'battery_capacity_mah', 'satellites', 'battery']:
                sql_type = "INTEGER"
            elif col in ['lat', 'lon', 'activity_score', 'temperature', 'accuracy', 'horiz_accuracy', 'altitude', 'baro_m', 'altitude_gain', 'speed_kmh', 'heading_deg']:
                sql_type = "FLOAT"
            elif col in ['wifi_aps']:
                sql_type = "JSON"
            elif col in ['is_predicted']:
                sql_type = "BOOLEAN"
            else:
                sql_type = "VARCHAR(50)"

            print(
                f"ALTER TABLE locations ADD COLUMN IF NOT EXISTS {col} {sql_type};")


if __name__ == "__main__":
    check_schema()
