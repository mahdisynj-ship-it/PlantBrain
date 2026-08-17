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


def get_plants(
    session: Session,
) -> list[Plant]:
    return session.query(Plant).order_by(Plant.id).all()


def get_plant_by_id(
    session: Session,
    plant_id: int,
) -> Plant | None:
    return session.get(Plant, plant_id)