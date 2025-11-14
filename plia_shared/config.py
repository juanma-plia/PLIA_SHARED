from pydantic_settings import BaseSettings
from typing import List


class BaseAPISettings(BaseSettings):
    """Configuración compartida entre microservicios"""

    PROJECT_ID: str = "plia-ai"
    LOCATION: str = "us-central1"

    API_KEY: str = 'AIzaSyCCa2dQ0aN4NIkyUBbXmFDc5UzvRStj9wU'

    CORS_ORIGINS: List[str] = ["*"]
