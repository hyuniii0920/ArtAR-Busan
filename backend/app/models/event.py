import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, gen_uuid


class Event(TimestampMixin, Base):
    __tablename__ = "event"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    exhibition_hall_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    organizer_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    theme: Mapped["EventTheme | None"] = relationship(
        back_populates="event", uselist=False, cascade="all, delete-orphan"
    )
    venues: Mapped[list["Venue"]] = relationship(  # noqa: F821
        back_populates="event", cascade="all, delete-orphan"
    )
    visit_logs: Mapped[list["VisitLog"]] = relationship(  # noqa: F821
        back_populates="event"
    )


class EventTheme(TimestampMixin, Base):
    __tablename__ = "event_theme"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=gen_uuid)
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("event.id", ondelete="CASCADE"), unique=True
    )
    primary_color: Mapped[str] = mapped_column(String(7), default="#000000")
    secondary_color: Mapped[str] = mapped_column(String(7), default="#FFFFFF")
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    app_name: Mapped[str] = mapped_column(String(100), default="ArtAR")
    font_family: Mapped[str] = mapped_column(String(50), default="Pretendard")
    hero_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationship
    event: Mapped["Event"] = relationship(back_populates="theme")
