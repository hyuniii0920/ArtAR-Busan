import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import I18nField

URL_PATTERN = r"^https?://[^\s]+$"
MediaType = Literal["image", "video", "audio", "model3d"]


class ArtworkBase(BaseModel):
    title_i18n: I18nField
    description_i18n: I18nField = Field(default_factory=I18nField)
    artist: str | None = Field(default=None, max_length=200)
    marker_image_url: str | None = Field(default=None, pattern=URL_PATTERN)
    media_url: str | None = Field(default=None, pattern=URL_PATTERN)
    media_type: MediaType = "image"
    sort_order: int = Field(default=0, ge=0)
    is_active: bool = True


class ArtworkCreate(ArtworkBase):
    pass


class ArtworkUpdate(BaseModel):
    title_i18n: I18nField | None = None
    description_i18n: I18nField | None = None
    artist: str | None = Field(default=None, max_length=200)
    marker_image_url: str | None = Field(default=None, pattern=URL_PATTERN)
    media_url: str | None = Field(default=None, pattern=URL_PATTERN)
    media_type: MediaType | None = None
    sort_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ArtworkResponse(ArtworkBase):
    id: uuid.UUID
    code: int | None = None  # QR에 인코딩되는 정수 식별자 (자동 채번)
    qr_url: str | None = None  # QR에 담을 완성된 딥링크 URL ({base}/api/works/{code})
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
