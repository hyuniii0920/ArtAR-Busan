import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import gen_uuid, utcnow


class Artwork(Base):
    __tablename__ = "artwork"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=gen_uuid)
    venue_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("venue.id", ondelete="CASCADE"), index=True
    )
    title_i18n: Mapped[dict] = mapped_column(JSONB, default=dict)
    description_i18n: Mapped[dict] = mapped_column(JSONB, default=dict)
    artist: Mapped[str | None] = mapped_column(String(200), nullable=True)
    marker_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_type: Mapped[str] = mapped_column(String(20), default="image")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )

    # Relationship
    venue: Mapped["Venue"] = relationship(back_populates="artworks")  # noqa: F821
