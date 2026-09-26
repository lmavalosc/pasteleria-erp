import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Núcleo Contable y DTE API"
    VERSION: str = "1.0.0-fase1"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://nucleo:nucleo@localhost:5432/nucleo",
    )
    STORAGE_DIR: Path = Path("storage/documents")

    # Proveedor SII: "stub" para local/CI, "sii" para producción
    SII_PROVIDER: str = "stub"
    SII_ENV: str = "certificacion"  # 'certificacion' o 'produccion'

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
