from sqlalchemy.orm import Session

from app.database.models import PlantEvent, WeatherSnapshot
from app.schemas.weather_snapshot import (
    CreateWeatherSnapshot,
    UpdateWeatherSnapshot,
)


def create_weather_snapshot(
    session: Session,
    event_id: int,
    data: CreateWeatherSnapshot,
) -> WeatherSnapshot:
    event = session.get(PlantEvent, event_id)

    if event is None:
        raise ValueError(f"Event with id {event_id} not found")

    existing_snapshot = (
        session.query(WeatherSnapshot)
        .filter(WeatherSnapshot.event_id == event_id)
        .first()
    )

    if existing_snapshot is not None:
        raise ValueError(
            f"Weather snapshot for event id {event_id} already exists"
        )

    snapshot = WeatherSnapshot(
        event_id=event_id,
        temperature=data.temperature,
        humidity=data.humidity,
        weather_condition=data.weather_condition,
        recorded_at=data.recorded_at,
        source=data.source,
    )

    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)

    return snapshot


def get_weather_snapshot_by_event_id(
    session: Session,
    event_id: int,
) -> WeatherSnapshot | None:
    return (
        session.query(WeatherSnapshot)
        .filter(WeatherSnapshot.event_id == event_id)
        .first()
    )


def update_weather_snapshot(
    session: Session,
    event_id: int,
    data: UpdateWeatherSnapshot,
) -> WeatherSnapshot | None:
    snapshot = get_weather_snapshot_by_event_id(
        session=session,
        event_id=event_id,
    )

    if snapshot is None:
        return None

    update_data = data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(snapshot, field, value)

    session.commit()
    session.refresh(snapshot)

    return snapshot


def delete_weather_snapshot(
    session: Session,
    event_id: int,
) -> bool:
    snapshot = get_weather_snapshot_by_event_id(
        session=session,
        event_id=event_id,
    )

    if snapshot is None:
        return False

    session.delete(snapshot)
    session.commit()

    return True