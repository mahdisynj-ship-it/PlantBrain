from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class PlantEvent(Base):
    __tablename__ = "plant_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    plant_id: Mapped[int] = mapped_column(
        ForeignKey("plants.id"),
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    unit: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    event_metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    plant: Mapped["Plant"] = relationship(
        back_populates="events",
    )