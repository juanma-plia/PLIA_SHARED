import redis.asyncio as redis
from typing import Optional, Any
import asyncio
import logging
import orjson
from functools import lru_cache

from plia_shared.config import BaseAPISettings

logger = logging.getLogger(__name__)

_redis_client: Optional[redis.Redis] = None
_lock = asyncio.Lock()


@lru_cache()
def get_settings() -> BaseAPISettings:
    """Obtiene settings (cached)"""
    return BaseAPISettings()


class RedisCacheService:
    """Servicio de cache Redis con métodos helper"""

    def __init__(self, client: redis.Redis):
        self.client = client

    async def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del cache y lo deserializa"""
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            return orjson.loads(value)
        except Exception as e:
            logger.warning(f"Redis get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Guarda un valor en el cache con serialización JSON"""
        try:
            serialized = orjson.dumps(value)
            return await self.client.set(key, serialized, ex=ex)
        except Exception as e:
            logger.warning(f"Redis set error for key {key}: {e}")
            return False

    async def delete(self, *keys: str) -> int:
        """Elimina una o más claves del cache"""
        try:
            return await self.client.delete(*keys)
        except Exception as e:
            logger.warning(f"Redis delete error for keys {keys}: {e}")
            return 0

    async def delete_pattern(self, pattern: str) -> int:
        """Elimina todas las claves que coincidan con el patrón"""
        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Redis delete_pattern error for pattern {pattern}: {e}")
            return 0

    async def close(self):
        """Cierra la conexión Redis"""
        try:
            await self.client.close()
        except Exception as e:
            logger.warning(f"Error closing Redis connection: {e}")


async def get_redis_client() -> Optional[RedisCacheService]:
    """
    Obtiene el cliente Redis singleton.
    Retorna None si Redis no está configurado.
    """
    global _redis_client

    settings = get_settings()

    if not settings.REDIS_HOST:
        logger.debug("Redis not configured (REDIS_HOST not set)")
        return None

    async with _lock:
        if _redis_client is None:
            try:
                _redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    password=settings.REDIS_PASSWORD,
                    db=settings.REDIS_DB,
                    ssl=settings.REDIS_USE_TLS,
                    decode_responses=False,  # Usamos orjson para serialización
                )
                # Test connection
                await _redis_client.ping()
                logger.info(
                    f"Redis client initialized: {settings.REDIS_HOST}:{settings.REDIS_PORT}"
                )
            except Exception as e:
                logger.error(f"Failed to initialize Redis client: {e}")
                _redis_client = None
                return None

    return RedisCacheService(_redis_client)


async def cache_get(key: str) -> Optional[Any]:
    """Helper para obtener un valor del cache"""
    cache = await get_redis_client()
    if cache is None:
        return None
    return await cache.get(key)


async def cache_set(key: str, value: Any, ex: Optional[int] = None) -> bool:
    """Helper para guardar un valor en el cache"""
    cache = await get_redis_client()
    if cache is None:
        return False
    return await cache.set(key, value, ex=ex)


async def cache_delete(*keys: str) -> int:
    """Helper para eliminar claves del cache"""
    cache = await get_redis_client()
    if cache is None:
        return 0
    return await cache.delete(*keys)

