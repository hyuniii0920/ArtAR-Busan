import uuid

from pydantic import BaseModel, Field

from app.schemas.common import I18nField


class VenueBase(BaseModel):
    name_i18n: I18nField
    lat: float
    lng: float
    description_i18n: I18nField = Field(default_factory=I18nField)
    address: str | None = Field(default=None, max_length=500)
    sort_order: int = 0
    is_active: bool = True


class VenueCreate(VenueBase):
    pass


class VenueUpdate(BaseModel):
    name_i18n: I18nField | None = None
    lat: float | None = None
    lng: float | None = None
    description_i18n: I18nField | None = None
    address: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class VenueResponse(VenueBase):
    id: uuid.UUID
    event_id: uuid.UUID
    artwork_count: int = 0

    model_config = {"from_attributes": True}


class VenueLocalizedResponse(BaseModel):
    """모바일 앱용 — 특정 언어로 추출된 응답"""

    id: uuid.UUID
    event_id: uuid.UUID
    name: str
    lat: float
    lng: float
    description: str
    address: str | None
    sort_order: int
    artwork_count: int = 0
