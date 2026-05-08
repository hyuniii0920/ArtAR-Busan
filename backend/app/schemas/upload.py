from typing import Literal

from pydantic import BaseModel, Field

ContentType = Literal["image/jpeg", "image/png", "image/webp", "image/gif"]


class SignedUrlRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: ContentType


class SignedUrlResponse(BaseModel):
    upload_url: str
    public_url: str
    key: str
    content_type: str
    expires_in_minutes: int
