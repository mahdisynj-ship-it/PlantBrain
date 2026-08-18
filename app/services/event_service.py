from sqlalchemy.orm import Session

from app.database.models import Plant, PlantEvent
from app.schemas.plant_event import CreatePlantEvent, UpdatePlantEvent


def create_event(
    session: Session,
    plant_id: int,
    data: CreatePlantEvent,
) -> PlantEvent:
    plant = session.get(Plant, plant_id)

    if plant is None:
        raise ValueError(f"Plant with id {plant_id} not found")

    event = PlantEvent(
        plant_id=plant_id,
        event_type=data.event_type,
        occurred_at=data.occurred_at,
        notes=data.notes,
        amount=data.amount,
        unit=data.unit,
        event_metadata=data.event_metadata,
    )

    session.add(event)
    session.commit()
    session.refresh(event)

    return event


def get_plant_events(
    session: Session,
    plant_id: int,
) -> list[PlantEvent]:
    return (
        session.query(PlantEvent)
        .filter(PlantEvent.plant_id == plant_id)
        .order_by(PlantEvent.id.desc())
        .all()
    )


def get_event_by_id(
    session: Session,
    event_id: int,
) -> PlantEvent | None:
    return session.get(PlantEvent, event_id)


def update_event(
    session: Session,
    event_id: int,
    data: UpdatePlantEvent,
) -> PlantEvent | None:
    event = session.get(PlantEvent, event_id)

    if event is None:
        return None

    update_data = data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(event, field, value)

    session.commit()
    session.refresh(event)

    return event


def delete_event(
    session: Session,
    event_id: int,
) -> bool:
    event = session.get(PlantEvent, event_id)

    if event is None:
        return False

    session.delete(event)
    session.commit()

    return True