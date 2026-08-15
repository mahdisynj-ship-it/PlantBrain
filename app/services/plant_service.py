from datetime import date, datetime

from sqlalchemy.orm import Session

from app.database.models import Plant


def create_plant(
    session: Session,
    name: str,
    scientific_name: str | None = None,
    common_name: str | None = None,
    species: str | None = None,
    acquired_at: date | None = None,
    location: str | None = None,
    status: str = "active",
    notes: str | None = None,
) -> Plant:
    plant = Plant(
        name=name,
        scientific_name=scientific_name,
        common_name=common_name,
        species=species,
        acquired_at=acquired_at,
        location=location,
        status=status,
        notes=notes,
    )

    session.add(plant)
    session.commit()
    session.refresh(plant)

    return plant