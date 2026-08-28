from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Plant(Base):
    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    scientific_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    common_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    species: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    acquired_at: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    place_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "places.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    place: Mapped["Place | None"] = relationship(
        "Place",
        back_populates="plants",
    )

    events: Mapped[list["PlantEvent"]] = relationship(
        "PlantEvent",
        back_populates="plant",
        cascade="all, delete-orphan",
    )