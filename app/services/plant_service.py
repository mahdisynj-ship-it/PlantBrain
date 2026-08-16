from sqlalchemy.orm import Session

from app.database.models import Plant
from app.schemas.plant import CreatePlant


def create_plant(
    session: Session,
    data: CreatePlant,
) -> Plant:
    plant = Plant(
        name=data.name,
        scientific_name=data.scientific_name,
        common_name=data.common_name,
        species=data.species,
        acquired_at=data.acquired_at,
        location=data.location,
        status=data.status,
        notes=data.notes,
    )

    session.add(plant)
    session.commit()
    session.refresh(plant)

    return plant