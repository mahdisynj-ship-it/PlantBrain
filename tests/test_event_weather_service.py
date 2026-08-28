from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from app.database.models import (
    Place,
    Plant,
    PlantEvent,
    WeatherSnapshot,
)
from app.services.event_weather_service import (
    create_weather_for_event,
)
from app.services.weather_provider import WeatherData


def create_place(
    db_session,
    name="Home",
    city="Lahijan",
    latitude=37.2073,
    longitude=50.0039,
    timezone_name="Asia/Tehran",
):
    place = Place(
        name=name,
        city=city,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone_name,
    )

    db_session.add(place)
    db_session.commit()
    db_session.refresh(place)

    return place


def create_plant(
    db_session,
    place_id=None,
    name="فیکوس",
):
    plant = Plant(
        name=name,
        place_id=place_id,
    )

    db_session.add(plant)
    db_session.commit()
    db_session.refresh(plant)

    return plant


def create_event(
    db_session,
    plant_id,
    occurred_at=None,
):
    if occurred_at is None:
        occurred_at = datetime(
            2026,
            8,
            28,
            6,
            0,
        )

    event = PlantEvent(
        plant_id=plant_id,
        event_type="watering",
        occurred_at=occurred_at,
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    return event


@patch(
    "app.services.event_weather_service.get_weather_for_time"
)
def test_create_weather_for_event(
    mock_get_weather_for_time,
    db_session,
):
    place = create_place(
        db_session,
    )

    plant = create_plant(
        db_session,
        place_id=place.id,
    )

    event = create_event(
        db_session,
        plant_id=plant.id,
    )

    mock_get_weather_for_time.return_value = WeatherData(
        temperature=23.5,
        humidity=72,
        weather_condition="partly_cloudy",
        recorded_at=datetime(
            2026,
            8,
            28,
            6,
            0,
        ),
        source="open-meteo",
    )

    snapshot = create_weather_for_event(
        session=db_session,
        event_id=event.id,
    )

    assert snapshot.id is not None
    assert snapshot.event_id == event.id
    assert snapshot.temperature == 23.5
    assert snapshot.humidity == 72
    assert (
        snapshot.weather_condition
        == "partly_cloudy"
    )
    assert snapshot.source == "open-meteo"

    assert snapshot.recorded_at == datetime(
        2026,
        8,
        28,
        6,
        0,
    )

    assert snapshot.recorded_at.tzinfo is None

    mock_get_weather_for_time.assert_called_once()

    _, kwargs = (
        mock_get_weather_for_time.call_args
    )

    assert kwargs["latitude"] == 37.2073
    assert kwargs["longitude"] == 50.0039
    assert (
        kwargs["timezone_name"]
        == "Asia/Tehran"
    )

    assert kwargs["occurred_at"].replace(
        tzinfo=None,
    ) == datetime(
        2026,
        8,
        28,
        9,
        30,
    )

    assert (
        kwargs["occurred_at"].utcoffset()
        == timedelta(
            hours=3,
            minutes=30,
        )
    )


def test_create_weather_for_missing_event(
    db_session,
):
    with pytest.raises(
        ValueError,
        match="Event with id 999 not found",
    ):
        create_weather_for_event(
            session=db_session,
            event_id=999,
        )


def test_create_weather_for_event_without_place(
    db_session,
):
    plant = create_plant(
        db_session,
    )

    event = create_event(
        db_session,
        plant_id=plant.id,
    )

    with pytest.raises(
        ValueError,
        match=(
            f"Plant with id {plant.id} "
            "has no place"
        ),
    ):
        create_weather_for_event(
            session=db_session,
            event_id=event.id,
        )


def test_create_weather_for_event_without_coordinates(
    db_session,
):
    place = create_place(
        db_session,
        latitude=None,
        longitude=None,
    )

    plant = create_plant(
        db_session,
        place_id=place.id,
    )

    event = create_event(
        db_session,
        plant_id=plant.id,
    )

    with pytest.raises(
        ValueError,
        match=(
            f"Place with id {place.id} "
            "has no coordinates"
        ),
    ):
        create_weather_for_event(
            session=db_session,
            event_id=event.id,
        )


def test_create_weather_for_event_with_existing_snapshot(
    db_session,
):
    place = create_place(
        db_session,
    )

    plant = create_plant(
        db_session,
        place_id=place.id,
    )

    event = create_event(
        db_session,
        plant_id=plant.id,
    )

    snapshot = WeatherSnapshot(
        event_id=event.id,
        temperature=20.0,
        humidity=60,
        weather_condition="clear",
        recorded_at=datetime(
            2026,
            8,
            28,
            6,
            0,
        ),
        source="test",
    )

    db_session.add(snapshot)
    db_session.commit()

    with pytest.raises(
        ValueError,
        match=(
            f"Weather snapshot for event id "
            f"{event.id} already exists"
        ),
    ):
        create_weather_for_event(
            session=db_session,
            event_id=event.id,
        )