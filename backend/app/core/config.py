from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "YouTube Video Splitter Platform"
    API_V1_STR: str = "/api/v1"
    
    # Base Storage Path
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    TEMP_DIR: Path = BASE_DIR / "temp"
    DEFAULT_DOWNLOAD_DIR: Path = Path(r"C:\Users\ABC\OneDrive\Desktop\Youtube\Download")
    
    # Safety Limits
    MAX_VIDEO_DURATION_SECONDS: int = 14400  # 4 hours max
    MAX_FILE_SIZE_BYTES: int = 2 * 1024 * 1024 * 1024  # 2 GB max
    MIN_SPLIT_PARTS: int = 2
    MAX_SPLIT_PARTS: int = 50
    
    # Job Cleanup
    CLEANUP_INTERVAL_MINUTES: int = 15
    JOB_EXPIRATION_MINUTES: int = 60
    
    # Allowed CORS Origins
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
try:
    settings.DEFAULT_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass
