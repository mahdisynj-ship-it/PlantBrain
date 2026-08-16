from sqlalchemy.orm import Session

from app.database.models import Plant, PlantEvent
from app.schemas.plant_event import CreatePlantEvent


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