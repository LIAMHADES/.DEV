"""
Seed script to populate initial Breeds database.
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Breed


def seed_breeds():
    db = SessionLocal()

    # List of 10 seeds as requested
    breeds_data = [
        {"name": "Mestizo", "size_category": "Medium", "avg_weight_kg": 20.0,
            "avg_height_cm": 50.0, "activity_multiplier": 1.2, "imc_min": 18.0, "imc_max": 25.0},
        {"name": "Labrador Retriever", "size_category": "Large", "avg_weight_kg": 30.0,
            "avg_height_cm": 57.0, "activity_multiplier": 1.4, "imc_min": 20.0, "imc_max": 28.0},
        {"name": "Pitbull", "size_category": "Medium", "avg_weight_kg": 25.0,
            "avg_height_cm": 48.0, "activity_multiplier": 1.5, "imc_min": 22.0, "imc_max": 30.0},
        {"name": "Border Collie", "size_category": "Medium", "avg_weight_kg": 18.0,
            "avg_height_cm": 50.0, "activity_multiplier": 1.8, "imc_min": 17.0, "imc_max": 23.0},
        {"name": "Pastor Alemán", "size_category": "Large", "avg_weight_kg": 35.0,
            "avg_height_cm": 62.0, "activity_multiplier": 1.5, "imc_min": 21.0, "imc_max": 29.0},
        {"name": "Golden Retriever", "size_category": "Large", "avg_weight_kg": 30.0,
            "avg_height_cm": 56.0, "activity_multiplier": 1.4, "imc_min": 20.0, "imc_max": 28.0},
        {"name": "Husky Siberiano", "size_category": "Large", "avg_weight_kg": 23.0,
            "avg_height_cm": 55.0, "activity_multiplier": 1.6, "imc_min": 18.0, "imc_max": 25.0},
        {"name": "Beagle", "size_category": "Small", "avg_weight_kg": 10.0,
            "avg_height_cm": 35.0, "activity_multiplier": 1.3, "imc_min": 16.0, "imc_max": 24.0},
        {"name": "Bulldog Francés", "size_category": "Small", "avg_weight_kg": 11.0,
            "avg_height_cm": 30.0, "activity_multiplier": 1.1, "imc_min": 24.0, "imc_max": 32.0},
        {"name": "Chihuahua", "size_category": "Toy", "avg_weight_kg": 2.0,
            "avg_height_cm": 20.0, "activity_multiplier": 1.1, "imc_min": 14.0, "imc_max": 20.0},
    ]

    for data in breeds_data:
        existing = db.query(Breed).filter(Breed.name == data["name"]).first()
        if not existing:
            breed = Breed(**data)
            db.add(breed)

    db.commit()
    db.close()
    print("Breeds seeded successfully.")


if __name__ == "__main__":
    seed_breeds()
