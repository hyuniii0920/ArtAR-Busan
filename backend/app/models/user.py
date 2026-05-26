import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, gen_uuid

ROLE_SUPER_ADMIN = "SUPER_ADMIN"
ROLE_MUSEUM = "MUSEUM"

STATUS_PENDING = "PENDING_MUSEUM"
STATUS_APPROVED = "APPROVED_MUSEUM"
STATUS_REJECTED = "REJECTED_MUSEUM"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default=ROLE_MUSEUM)
    museum_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    museum_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact: Mapped[str | None] = mapped_column(String(100), nullable=True)
    proof_file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    proof_file_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
