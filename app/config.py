from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Secrets come from .env or the process environment. Keep only a local,
    # non-sensitive SQLite fallback so importing the app remains possible.
    DATABASE_URL: str = "sqlite:///./ares_dev.db"
    SECRET_KEY: str = ""
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
    API_KEY: str = ""  # Header X-API-Key
    DEVICE_KEY: str = ""  # Header X-Device-Key for device polling
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173"]  # Restrict to dashboard
    WATCHDOG_ENABLED: bool = True

    # Device command defaults
    COMMAND_TTL_MINUTES: int = 10

    # Commands
    PING_TTL_SECONDS: int = 120
    PING_COOLDOWN_SECONDS: int = 60

    # Nutrition vision analysis (Gemini multimodal). Optional:
    # if empty, the /nutrition/analyze-declared endpoint works and the
    # photo→macros extraction is disabled until a key is provided.
    VISION_API_KEY: str = ""
    VISION_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    VISION_COST_PER_CALL_EUR: float = 0.001

    class Config:
        env_file = ".env"


settings = Settings()
