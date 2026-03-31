import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class VisitCreate(BaseModel):
    event_id: uuid.UUID
    venue_id: uuid.UUID | None = None
    artwork_id: uuid.UUID | None = None
    lang: str = Field(default="ko", pattern=r"^(ko|en|jp|cn)$")
    os: str = Field(default="unknown", max_length=20)
    device_hash: str | None = Field(default=None, max_length=64)


class VisitResponse(BaseModel):
    id: uuid.UUID
    event_id: uuid.UUID | None
    venue_id: uuid.UUID | None
    artwork_id: uuid.UUID | None
    visited_at: datetime
    lang: str
    os: str

    model_config = {"from_attributes": True}


class VisitCountResponse(BaseModel):
    event_slug: str
    device_hash: str
    unique_venue_count: int
