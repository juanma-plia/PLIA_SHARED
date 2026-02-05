from pydantic import BaseModel, Field, field_validator


class ProfileUUIDMixin(BaseModel):
    """Mixin para requests que requieren profile_uuid"""

    profile_uuid: str = Field(
        ..., min_length=10, max_length=100, description="UUID del perfil del usuario"
    )

    @field_validator("profile_uuid")
    @classmethod
    def validate_profile_uuid(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("profile_uuid no puede estar vacío")
        return v.strip()


class SerieUUIDMixin(BaseModel):
    """Mixin para requests que requieren serie_uuid"""

    serie_uuid: str = Field(
        ..., min_length=10, max_length=100, description="UUID de la serie"
    )

    @field_validator("serie_uuid")
    @classmethod
    def validate_serie_uuid(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("serie_uuid no puede estar vacío")
        return v.strip()


class ProfileRequest(ProfileUUIDMixin):
    """Request para obtener perfil"""

    pass


class SeriesRequest(ProfileUUIDMixin):
    """Request para listar series disponibles"""

    pass


class CharactersRequest(ProfileUUIDMixin, SerieUUIDMixin):
    """Request para obtener personajes de una serie"""

    pass


class ScenesRequest(ProfileUUIDMixin, SerieUUIDMixin):
    """Request para obtener escenas de una serie"""

    pass


class LocationsRequest(ProfileUUIDMixin, SerieUUIDMixin):
    """Request para obtener locaciones de una serie"""

    pass


class DocsRequest(ProfileUUIDMixin, SerieUUIDMixin):
    """Request para obtener documentos de una serie"""

    pass


class ShootplansRequest(ProfileUUIDMixin, SerieUUIDMixin):
    """Request para obtener shootplans de una serie"""

    pass
