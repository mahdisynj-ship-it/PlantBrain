from sqlalchemy.orm import Session

from app.database.models import (
    Place,
    Plant,
    PlantEvent,
    WeatherSnapshot,
)
from app.schemas.weather_snapshot import (
    CreateWeatherSnapshot,
    UpdateWeatherSnapshot,
)
from app.utils.datetime_utils import (
    local_datetime_to_utc_naive,
)


def create_weather_snapshot(
    session: Session,
    event_id: int,
    data: CreateWeatherSnapshot,
) -> WeatherSnapshot:
    event = session.get(
        PlantEvent,
        event_id,
    )

    if event is None:
        raise ValueError(
            f"Event with id {event_id} not found"
        )

    existing_snapshot = (
        session.query(WeatherSnapshot)
        .filter(
            WeatherSnapshot.event_id == event_id,
        )
        .first()
    )

    if existing_snapshot is not None:
        raise ValueError(
            f"Weather snapshot for event id "
            f"{event_id} already exists"
        )

    timezone_name = _get_event_timezone_name(
        session=session,
        event=event,
    )

    recorded_at_utc = (
        local_datetime_to_utc_naive(
            value=data.recorded_at,
            timezone_name=timezone_name,
        )
    )

    snapshot = WeatherSnapshot(
        event_id=event_id,
        temperature=data.temperature,
        humidity=data.humidity,
        weather_condition=(
            data.weather_condition
        ),
        recorded_at=recorded_at_utc,
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
        .filter(
            WeatherSnapshot.event_id == event_id,
        )
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

    if "recorded_at" in update_data:
        event = session.get(
            PlantEvent,
            event_id,
        )

        if event is None:
            raise ValueError(
                f"Event with id {event_id} not found"
            )

        timezone_name = (
            _get_event_timezone_name(
                session=session,
                event=event,
            )
        )

        update_data["recorded_at"] = (
            local_datetime_to_utc_naive(
                value=update_data[
                    "recorded_at"
                ],
                timezone_name=(
                    timezone_name
                ),
            )
        )

    for field, value in update_data.items():
        setattr(
            snapshot,
            field,
            value,
        )

    session.commit()
    session.refresh(snapshot)

    return snapshot


def delete_weather_snapshot(
    session: Session,
    event_id: int,
) -> bool:
    snapshot = (
        get_weather_snapshot_by_event_id(
            session=session,
            event_id=event_id,
        )
    )

    if snapshot is None:
        return False

    session.delete(snapshot)
    session.commit()

    return True


def _get_event_timezone_name(
    session: Session,
    event: PlantEvent,
) -> str:
    plant = session.get(
        Plant,
        event.plant_id,
    )

    if plant is None:
        return "UTC"

    if plant.place_id is None:
        return "UTC"

    place = session.get(
        Place,
        plant.place_id,
    )

    if place is None:
        return "UTC"

    return place.timezone