from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int


class Scene(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")

    uuid: str
    episode_uuid: str
    serie_uuid: Optional[str] = None
    scene_number: Optional[str] = None
    description: Optional[str] = None
    order: int = 0
    ai: Optional[Any] = None


class Location(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")

    uuid: str
    serie_uuid: str
    name: str
    type: Optional[str] = None
    order: int = 0


class Document(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")

    uuid: str
    serie_uuid: str
    title: str
    type: Optional[str] = None
    order: int = 0


class Shootplan(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")

    uuid: str
    serie_uuid: str
    title: str
    order: int = 0


class ScenesListResponse(BaseModel):
    scenes: List[Scene]
    total: int
    serie_uuid: str


class LocationsListResponse(BaseModel):
    locations: List[Location]
    total: int
    serie_uuid: str


class DocsListResponse(BaseModel):
    docs: List[Document]
    total: int
    serie_uuid: str


class ShootplansListResponse(BaseModel):
    shootplans: List[Shootplan]
    total: int
    serie_uuid: str
