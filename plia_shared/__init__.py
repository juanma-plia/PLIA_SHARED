from .config import BaseAPISettings

__version__ = "0.1.0"

from .core.auth import validate_api_key, get_settings
from .core.errors import (
    PliaAPIException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ProfileNotFoundException,
    SerieNotFoundException,
    UnauthorizedSerieAccessException,
    InvalidAPIKeyException,
    FirestoreException,
)
from .core.security import ACLService, get_acl_service_dep

from .database.firestore import FirestoreService, get_firestore_service

from .models.requests import (
    ProfileRequest,
    SeriesRequest,
    CharactersRequest,
    ScenesRequest,
    LocationsRequest,
    DocsRequest,
    ShootplansRequest,
)
from .models.responses import (
    ErrorResponse,
    Scene,
    Location,
    Document,
    Shootplan,
    ScenesListResponse,
    LocationsListResponse,
    DocsListResponse,
    ShootplansListResponse,
)

__all__ = [
    "__version__",
    # Config
    "BaseAPISettings",
    # Auth / Security
    "validate_api_key",
    "get_settings",
    "ACLService",
    "get_acl_service_dep",
    # Errors
    "PliaAPIException",
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
    "NotFoundException",
    "ProfileNotFoundException",
    "SerieNotFoundException",
    "UnauthorizedSerieAccessException",
    "InvalidAPIKeyException",
    "FirestoreException",
    # Database
    "FirestoreService",
    "get_firestore_service",
    # Request models
    "ProfileRequest",
    "SeriesRequest",
    "CharactersRequest",
    "ScenesRequest",
    "LocationsRequest",
    "DocsRequest",
    "ShootplansRequest",
    # Response / domain models
    "ErrorResponse",
    "Scene",
    "Location",
    "Document",
    "Shootplan",
    "ScenesListResponse",
    "LocationsListResponse",
    "DocsListResponse",
    "ShootplansListResponse",
]
