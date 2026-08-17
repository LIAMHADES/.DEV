from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://ares_user:ares_secret@localhost:5432/ares_gps"
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week

    # Watchdog timers (minutes)
    WATCHDOG_WALKING_MINUTES: int = 5
    WATCHDOG_REST_MINUTES: int = 60

    # Geofence defaults
    GEOFENCE_TOLERANCE_M: float = 5.0
    GEOFENCE_COOLDOWN_MINUTES: int = 5
    GEOFENCE_CONFIRM_READINGS: int = 2

    # Security & Development
    DEV_MODE: bool = True  # Enable simulation endpoints
    API_KEY: str = "ares-secret-gateway-key"  # Header X-API-Key
    DEVICE_KEY: str = "ares-device-key"  # Header X-Device-Key for device polling
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173"]  # Restrict to dashboard
    WATCHDOG_ENABLED: bool = True

    # Device command defaults
    COMMAND_TTL_MINUTES: int = 10

    # Commands
    PING_TTL_SECONDS: int = 120
    PING_COOLDOWN_SECONDS: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
