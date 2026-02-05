from fastapi import Security, Depends
from fastapi.security import APIKeyHeader
from typing import Optional
from functools import lru_cache
from plia_shared.core.errors import InvalidAPIKeyException
from plia_shared.config import BaseAPISettings
import logging

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


@lru_cache()
def get_settings() -> BaseAPISettings:
    return BaseAPISettings()


async def validate_api_key(
    x_api_key: Optional[str] = Security(api_key_header),
    settings: BaseAPISettings = Depends(get_settings),
) -> str:
    if not x_api_key:
        logger.warning("Missing API key")
        raise InvalidAPIKeyException()

    # Strip espacios por seguridad
    x_api_key = x_api_key.strip()

    if x_api_key != settings.API_KEY:
        logger.warning("Invalid API key provided")
        raise InvalidAPIKeyException()

    return x_api_key
