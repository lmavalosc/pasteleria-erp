import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Maison du Delice - Core API"
    VERSION: str = "1.0.0-fase1"
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "super-secret-production-grade-jwt-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 dias
    
    # Storage settings
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "storage_data")))
    MAX_UPLOAD_SIZE_MB: int = 10
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
