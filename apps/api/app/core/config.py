import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_API_DIR = Path(__file__).resolve().parents[2]
_ENV_FILE = _API_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "Núcleo Contable y DTE API"
    version: str = "1.0.0-fase1"
    debug: bool = True

    database_url: str = (
        "postgresql+psycopg://nucleo:nucleo@localhost:5432/nucleo"
    )

    storage_local_dir: str = "var/uploads"

    cors_origins: list[str] = ["*"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            v_str = v.strip()
            if v_str.startswith("[") and v_str.endswith("]"):
                try:
                    return json.loads(v_str)
                except Exception:
                    pass
            return [i.strip() for i in v_str.split(",") if i.strip()]
        if isinstance(v, list):
            return v
        return ["*"]

    sii_enabled: bool = False
    sii_use_legacy: bool = False
    sii_environment: Literal["prueba", "produccion"] = "prueba"

    sii_cert_base64: str | None = None
    sii_cert_password: str | None = None
    sii_caf_base64: str | None = None

    # Autenticación y API
    api_v1_prefix: str = "/api/v1"
    openapi_url: str = "/api/v1/openapi.json"
    secret_key: str = "supersecretkey_dev_only_change_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # Compatibilidad con accesos en mayúsculas
    @property
    def PROJECT_NAME(self) -> str:
        return self.app_name

    @property
    def VERSION(self) -> str:
        return self.version

    @property
    def API_V1_PREFIX(self) -> str:
        return self.api_v1_prefix

    @property
    def DATABASE_URL(self) -> str:
        return self.database_url

    @property
    def STORAGE_LOCAL_DIR(self) -> Path:
        return Path(self.storage_local_dir)

    @property
    def STORAGE_DIR(self) -> Path:
        return Path(self.storage_local_dir)

    @property
    def SII_ENABLED(self) -> bool:
        return self.sii_enabled

    @property
    def SII_USE_LEGACY(self) -> bool:
        return self.sii_use_legacy

    @property
    def SII_ENVIRONMENT(self) -> str:
        return self.sii_environment

    @property
    def SII_PROVIDER(self) -> str:
        return "sii" if self.sii_enabled and self.sii_use_legacy else "stub"

    @property
    def SII_ENV(self) -> str:
        return self.sii_environment

    @property
    def SECRET_KEY(self) -> str:
        return self.secret_key

    @property
    def ALGORITHM(self) -> str:
        return self.algorithm

    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return self.access_token_expire_minutes

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
Path(settings.storage_local_dir).mkdir(parents=True, exist_ok=True)
