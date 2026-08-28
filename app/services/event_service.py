from sqlalchemy.orm import Session

from app.database.models import Place, Plant, PlantEvent
from app.schemas.plant_event import CreatePlantEvent, UpdatePlantEvent
from app.utils.datetime_utils import local_datetime_to_utc_naive


def create_event(
    session: Session,
    plant_id: int,
    data: CreatePlantEvent,
) -> PlantEvent:
    plant = session.get(
        Plant,
        plant_id,
    )

    if plant is None:
        raise ValueError(
            f"Plant with id {plant_id} not found"
        )

    timezone_name = _get_plant_timezone_name(
        session=session,
        plant=plant,
    )

    occurred_at_utc = local_datetime_to_utc_naive(
        value=data.occurred_at,
        timezone_name=timezone_name,
    )

    event = PlantEvent(
        plant_id=plant_id,
        event_type=data.event_type,
        occurred_at=occurred_at_utc,
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
        .filter(
            PlantEvent.plant_id == plant_id,
        )
        .order_by(
            PlantEvent.id.desc(),
        )
        .all()
    )


def get_event_by_id(
    session: Session,
    event_id: int,
) -> PlantEvent | None:
    return session.get(
        PlantEvent,
        event_id,
    )


def update_event(
    session: Session,
    event_id: int,
    data: UpdatePlantEvent,
) -> PlantEvent | None:
    event = session.get(
        PlantEvent,
        event_id,
    )

    if event is None:
        return None

    update_data = data.model_dump(
        exclude_unset=True,
    )

    if "occurred_at" in update_data:
        plant = session.get(
            Plant,
            event.plant_id,
        )

        if plant is None:
            raise ValueError(
                f"Plant with id {event.plant_id} not found"
            )

        timezone_name = _get_plant_timezone_name(
            session=session,
            plant=plant,
        )

        update_data["occurred_at"] = (
            local_datetime_to_utc_naive(
                value=update_data["occurred_at"],
                timezone_name=timezone_name,
            )
        )

    for field, value in update_data.items():
        setattr(
            event,
            field,
            value,
        )

    session.commit()
    session.refresh(event)

    return event


def delete_event(
    session: Session,
    event_id: int,
) -> bool:
    event = session.get(
        PlantEvent,
        event_id,
    )

    if event is None:
        return False

    session.delete(event)
    session.commit()

    return True


def _get_plant_timezone_name(
    session: Session,
    plant: Plant,
) -> str:
    if plant.place_id is None:
        return "UTC"

    place = session.get(
        Place,
        plant.place_id,
    )

    if place is None:
        return "UTC"

    return place.timezone