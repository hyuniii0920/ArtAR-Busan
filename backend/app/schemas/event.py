import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

URL_PATTERN = r"^https?://[^\s]+$"


# --- EventTheme ---
class EventThemeBase(BaseModel):
    primary_color: str = Field(default="#000000", pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary_color: str = Field(default="#FFFFFF", pattern=r"^#[0-9A-Fa-f]{6}$")
    logo_url: str | None = Field(default=None, pattern=URL_PATTERN)
    app_name: str = Field(default="ArtAR", max_length=100)
    font_family: str = Field(default="Pretendard", max_length=50)
    hero_image_url: str | None = Field(default=None, pattern=URL_PATTERN)


class EventThemeCreate(EventThemeBase):
    pass


class EventThemeResponse(EventThemeBase):
    id: uuid.UUID
    event_id: uuid.UUID

    model_config = {"from_attributes": True}


# --- Event ---
class EventBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    start_date: date
    end_date: date
    is_public: bool = False
    # 응답에서는 optional (기존 행은 값이 없을 수 있음)
    exhibition_hall_name: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=500)
    organizer_name: str | None = Field(default=None, max_length=200)
    memo: str | None = None

    @model_validator(mode="after")
    def _check_date_range(self) -> "EventBase":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class EventCreate(EventBase):
    # 생성 시에는 필수 (프론트 요청 스펙)
    exhibition_hall_name: str = Field(min_length=1, max_length=200)
    location: str = Field(min_length=1, max_length=500)
    organizer_name: str = Field(min_length=1, max_length=200)


class EventUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    start_date: date | None = None
    end_date: date | None = None
    is_public: bool | None = None
    exhibition_hall_name: str | None = Field(default=None, min_length=1, max_length=200)
    location: str | None = Field(default=None, min_length=1, max_length=500)
    organizer_name: str | None = Field(default=None, min_length=1, max_length=200)
    memo: str | None = None

    @model_validator(mode="after")
    def _check_date_range(self) -> "EventUpdate":
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError("end_date must be on or after start_date")
        return self


class EventResponse(EventBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    theme: EventThemeResponse | None = None
    venue_count: int = 0

    model_config = {"from_attributes": True}


class EventListResponse(EventBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    venue_count: int = 0

    model_config = {"from_attributes": True}
