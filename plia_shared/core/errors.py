"""
Excepciones personalizadas para toda la API
"""

from fastapi import HTTPException, status
from typing import Optional


class PliaAPIException(HTTPException):
    """Base exception para toda la API"""

    def __init__(
        self, detail: str, status_code: int = 500, headers: Optional[dict] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class BadRequestException(PliaAPIException):
    """Error 400 - Request inválido"""

    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class UnauthorizedException(PliaAPIException):
    """Error 401 - No autenticado"""

    def __init__(self, detail: str = "No autorizado"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(PliaAPIException):
    """Error 403 - Sin permisos"""

    def __init__(self, detail: str = "Acceso denegado"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundException(PliaAPIException):
    """Error 404 - Recurso no encontrado"""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            detail=f"{resource} '{identifier}' no encontrado",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ProfileNotFoundException(NotFoundException):
    """Profile no encontrado"""

    def __init__(self, profile_uuid: str):
        super().__init__("Profile", profile_uuid)


class SerieNotFoundException(NotFoundException):
    """Serie no encontrada"""

    def __init__(self, serie_uuid: str):
        super().__init__("Serie", serie_uuid)


class UnauthorizedSerieAccessException(ForbiddenException):
    """Usuario no tiene acceso a la serie"""

    def __init__(self, serie_uuid: str):
        super().__init__(f"No tienes acceso a la serie '{serie_uuid}'")


class InvalidAPIKeyException(UnauthorizedException):
    """API Key inválida"""

    def __init__(self):
        super().__init__("API Key inválida o faltante")


class FirestoreException(PliaAPIException):
    """Error de base de datos"""

    def __init__(self, detail: str, original_error: Optional[Exception] = None):
        error_msg = f"Error de base de datos: {detail}"
        if original_error:
            error_msg += f" ({str(original_error)})"
        super().__init__(detail=error_msg, status_code=500)
