import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import I18nField


class ArtworkBase(BaseModel):
    title_i18n: I18nField
    description_i18n: I18nField = Field(default_factory=I18nField)
    artist: str | None = Field(default=None, max_length=200)
    marker_image_url: str | None = None
    media_url: str | None = None
    media_type: str = Field(default="image", max_length=20)
    sort_order: int = 0
    is_active: bool = True


class ArtworkCreate(ArtworkBase):
    pass


class ArtworkUpdate(BaseModel):
    title_i18n: I18nField | None = None
    description_i18n: I18nField | None = None
    artist: str | None = None
    marker_image_url: str | None = None
    media_url: str | None = None
    media_type: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class ArtworkResponse(ArtworkBase):
    id: uuid.UUID
    venue_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ArtworkLocalizedResponse(BaseModel):
    """모바일 앱용 — 특정 언어로 추출된 응답"""

    id: uuid.UUID
    venue_id: uuid.UUID
    title: str
    description: str
    artist: str | None
    marker_image_url: str | None
    media_url: str | None
    media_type: str
    sort_order: int
