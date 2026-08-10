from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Plant(Base):
    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
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
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )