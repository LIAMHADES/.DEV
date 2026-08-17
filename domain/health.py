"""
Health and Nutrition formulas for ARES.
"""


def calculate_rer(weight_kg: float) -> float:
    """
    Resting Energy Requirement (RER).
    Formula: 70 * (body_weight_kg ^ 0.75)
    """
    if weight_kg <= 0:
        return 0.0
    return 70 * (weight_kg ** 0.75)


def calculate_der(rer: float, multiplier: float) -> float:
    """
    Daily Energy Requirement (DER).
    Formula: RER * multiplier
    """
    return rer * multiplier


def estimate_kcal_burned(weight_kg: float, distance_km: float) -> float:
    """
    Estimated kcal burned during a walk.
    Rough rule of thumb: 1.0 kcal per kg of body weight per km.
    Enhanced for dogs: approx 1.1 - 1.5 kcal/kg/km depending on intensity.
    """
    if weight_kg <= 0 or distance_km <= 0:
        return 0.0
    # Using 1.2 as a conservative average factor for dogs
    return weight_kg * distance_km * 1.2


def calculate_imc(weight_kg: float, height_cm: float) -> float:
    """
    Canine IMC (Body Mass Index).
    Simplified: weight_kg / (height_m^2)
    Note: Real canine BCS is often visual (1-9), but document suggests IMC ranges.
    """
    if weight_kg <= 0 or height_cm <= 0:
        return 0.0
    height_m = height_cm / 100.0
    return weight_kg / (height_m ** 2)
