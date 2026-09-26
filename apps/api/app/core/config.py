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
    STORAGE_LOCAL_DIR: Path = Path(os.getenv("STORAGE_LOCAL_DIR", "var/uploads"))

    # Configuración de integración SII
    SII_ENABLED: bool = False
    SII_USE_LEGACY: bool = False
    SII_ENVIRONMENT: str = "prueba"
    SII_CERT_BASE64: str | None = None
    SII_CERT_PASSWORD: str | None = None
    SII_CAF_BASE64: str | None = None

    # Alias y compatibilidad
    @property
    def STORAGE_DIR(self) -> Path:
        return self.STORAGE_LOCAL_DIR

    @property
    def SII_PROVIDER(self) -> str:
        return "sii" if self.SII_ENABLED and self.SII_USE_LEGACY else "stub"

    @property
    def SII_ENV(self) -> str:
        return self.SII_ENVIRONMENT

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
settings.STORAGE_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
