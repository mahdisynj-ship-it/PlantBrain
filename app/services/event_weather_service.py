from sqlalchemy.orm import Session

from app.database.models import Place, Plant, PlantEvent, WeatherSnapshot
from app.services.open_meteo_provider import get_weather_for_time


def create_weather_for_event(
    session: Session,
    event_id: int,
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
            f"Weather snapshot for event id {event_id} already exists"
        )

    plant = session.get(
        Plant,
        event.plant_id,
    )

    if plant is None:
        raise ValueError(
            f"Plant with id {event.plant_id} not found"
        )

    if plant.place_id is None:
        raise ValueError(
            f"Plant with id {plant.id} has no place"
        )

    place = session.get(
        Place,
        plant.place_id,
    )

    if place is None:
        raise ValueError(
            f"Place with id {plant.place_id} not found"
        )

    if (
        place.latitude is None
        or place.longitude is None
    ):
        raise ValueError(
            f"Place with id {place.id} has no coordinates"
        )

    weather_data = get_weather_for_time(
        latitude=place.latitude,
        longitude=place.longitude,
        occurred_at=event.occurred_at,
    )

    snapshot = WeatherSnapshot(
        event_id=event.id,
        temperature=weather_data.temperature,
        humidity=weather_data.humidity,
        weather_condition=weather_data.weather_condition,
        recorded_at=weather_data.recorded_at,
        source=weather_data.source,
    )

    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)

    return snapshot