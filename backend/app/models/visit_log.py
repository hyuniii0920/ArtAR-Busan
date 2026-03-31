import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import gen_uuid, utcnow


class VisitLog(Base):
    __tablename__ = "visit_log"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=gen_uuid)
    event_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("event.id", ondelete="SET NULL"), nullable=True, index=True
    )
    venue_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("venue.id", ondelete="SET NULL"), nullable=True
    )
    artwork_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("artwork.id", ondelete="SET NULL"), nullable=True
    )
    visited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    lang: Mapped[str] = mapped_column(String(5), default="ko")
    os: Mapped[str] = mapped_column(String(20), default="unknown")
    device_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Relationships
    event: Mapped["Event | None"] = relationship(  # noqa: F821
        back_populates="visit_logs"
    )
