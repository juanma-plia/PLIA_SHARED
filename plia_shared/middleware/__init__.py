"""
Middleware compartidos para todos los microservicios.
"""
from fastapi.middleware.gzip import GZipMiddleware


def setup_compression_middleware(app, minimum_size: int = 1000):
    """
    Configura compresión gzip para responses grandes.
    
    Args:
        app: Instancia de FastAPI
        minimum_size: Tamaño mínimo en bytes para comprimir (default: 1KB)
    
    Example:
        >>> from fastapi import FastAPI
        >>> from plia_shared.middleware import setup_compression_middleware
        >>> 
        >>> app = FastAPI()
        >>> setup_compression_middleware(app)
    """
    app.add_middleware(GZipMiddleware, minimum_size=minimum_size)


__all__ = ["setup_compression_middleware", "GZipMiddleware"]

