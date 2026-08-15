from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import PlantEvent


def create_event(
    session: Session,
    plant_id: int,
    event_type: str,
    occurred_at: datetime,
    notes: str | None = None,
    amount: float | None = None,
    unit: str | None = None,
    event_metadata: dict | None = None,
) -> PlantEvent:
    event = PlantEvent(
        plant_id=plant_id,
        event_type=event_type,
        occurred_at=occurred_at,
        notes=notes,
        amount=amount,
        unit=unit,
        event_metadata=event_metadata,
    )

    session.add(event)
    session.commit()
    session.refresh(event)

    return event