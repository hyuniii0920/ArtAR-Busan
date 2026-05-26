import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Role = Literal["SUPER_ADMIN", "MUSEUM"]
MuseumStatus = Literal["PENDING_MUSEUM", "APPROVED_MUSEUM", "REJECTED_MUSEUM"]


class UserResponse(BaseModel):
    """password_hash는 절대 노출하지 않는다."""

    id: uuid.UUID
    email: str
    role: Role
    museum_status: MuseumStatus | None = None
    museum_name: str | None = None
    contact: str | None = None
    proof_file_name: str | None = None
    proof_file_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenWithUser(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MuseumStatusUpdate(BaseModel):
    museum_status: MuseumStatus
