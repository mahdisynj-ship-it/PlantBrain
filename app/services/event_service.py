from sqlalchemy.orm import Session

from app.database.models import PlantEvent
from app.schemas.plant_event import CreatePlantEvent


def create_event(
    session: Session,
    data: CreatePlantEvent,
) -> PlantEvent:
    event = PlantEvent(
        plant_id=data.plant_id,
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