from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class BaseAPISettings(BaseSettings):
    """Configuración compartida entre microservicios"""

    PROJECT_ID: str = "plia-ai"
    LOCATION: str = "us-central1"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    API_KEY: Optional[str] = None

    CORS_ORIGINS: List[str] = ["*"]

    # Redis Configuration
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_USE_TLS: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
