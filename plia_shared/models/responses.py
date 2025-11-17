from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Any


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int


class Serie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    serie_uuid: str
    serie_title: str
    serie_initials: str = ""
    serie_type: str = "undefined"
    serie_stage: str = "undefined"
    serie_episodes: List[str] = Field(default_factory=list)
    serie_timestamp: int = 0
    shootplan_uuid: Optional[str] = None


class Character(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")

    uuid: str = Field(alias="uuid")
    serie_uuid: str
    name: str
    description: Optional[str] = None
    order: int = 0


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


class SeriesListResponse(BaseModel):
    series: List[Serie]
    total: int


class CharactersListResponse(BaseModel):
    characters: List[Character]
    total: int
    serie_uuid: str


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
