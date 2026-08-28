from sqlalchemy.orm import Session

from app.database.models import Place, Plant
from app.schemas.plant import CreatePlant, UpdatePlant


def create_plant(
    session: Session,
    data: CreatePlant,
) -> Plant:
    if data.place_id is not None:
        place = session.get(
            Place,
            data.place_id,
        )

        if place is None:
            raise ValueError(
                f"Place with id {data.place_id} not found"
            )

    plant = Plant(
        name=data.name,
        scientific_name=data.scientific_name,
        common_name=data.common_name,
        species=data.species,
        acquired_at=data.acquired_at,
        location=data.location,
        place_id=data.place_id,
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
    return (
        session.query(Plant)
        .order_by(Plant.id)
        .all()
    )


def get_plant_by_id(
    session: Session,
    plant_id: int,
) -> Plant | None:
    return session.get(Plant, plant_id)


def update_plant(
    session: Session,
    plant_id: int,
    data: UpdatePlant,
) -> Plant | None:
    plant = session.get(
        Plant,
        plant_id,
    )

    if plant is None:
        return None

    update_data = data.model_dump(
        exclude_unset=True,
    )

    if "place_id" in update_data:
        place_id = update_data["place_id"]

        if place_id is not None:
            place = session.get(
                Place,
                place_id,
            )

            if place is None:
                raise ValueError(
                    f"Place with id {place_id} not found"
                )

    for field, value in update_data.items():
        setattr(
            plant,
            field,
            value,
        )

    session.commit()
    session.refresh(plant)

    return plant


def delete_plant(
    session: Session,
    plant_id: int,
) -> bool:
    plant = session.get(
        Plant,
        plant_id,
    )

    if plant is None:
        return False

    session.delete(plant)
    session.commit()

    return True