import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import gen_uuid


class Venue(Base):
    __tablename__ = "venue"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=gen_uuid)
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("event.id", ondelete="CASCADE"), index=True
    )
    name_i18n: Mapped[dict] = mapped_column(JSONB, default=dict)
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    description_i18n: Mapped[dict] = mapped_column(JSONB, default=dict)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    event: Mapped["Event"] = relationship(back_populates="venues")  # noqa: F821
    artworks: Mapped[list["Artwork"]] = relationship(  # noqa: F821
        back_populates="venue", cascade="all, delete-orphan"
    )
