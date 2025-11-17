from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class BaseAPISettings(BaseSettings):
    """Configuración compartida entre microservicios"""

    PROJECT_ID: str = "plia-ai"
    LOCATION: str = "us-central1"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    API_KEY: str = "AIzaSyCCa2dQ0aN4NIkyUBbXmFDc5UzvRStj9wU"

    CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
