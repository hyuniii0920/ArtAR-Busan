import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


# --- EventTheme ---
class EventThemeBase(BaseModel):
    primary_color: str = Field(default="#000000", pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary_color: str = Field(default="#FFFFFF", pattern=r"^#[0-9A-Fa-f]{6}$")
    logo_url: str | None = None
    app_name: str = Field(default="ArtAR", max_length=100)
    font_family: str = Field(default="Pretendard", max_length=50)
    hero_image_url: str | None = None


class EventThemeCreate(EventThemeBase):
    pass


class EventThemeResponse(EventThemeBase):
    id: uuid.UUID
    event_id: uuid.UUID

    model_config = {"from_attributes": True}


# --- Event ---
class EventBase(BaseModel):
    name: str = Field(max_length=200)
    slug: str = Field(max_length=100, pattern=r"^[a-z0-9-]+$")
    start_date: date
    end_date: date
    is_public: bool = False


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    slug: str | None = Field(default=None, max_length=100, pattern=r"^[a-z0-9-]+$")
    start_date: date | None = None
    end_date: date | None = None
    is_public: bool | None = None


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
    venue_count: int = 0

    model_config = {"from_attributes": True}
