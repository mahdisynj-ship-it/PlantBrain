from datetime import datetime
from unittest.mock import patch

import pytest

from app.database.models import Place, Plant, PlantEvent
from app.services.event_weather_service import create_weather_for_event
from app.services.weather_provider import WeatherData


def create_place(
    db_session,
    name="خانه",
    latitude=37.2073,
    longitude=50.0039,
):
    place = Place(
        name=name,
        city="لاهیجان",
        latitude=latitude,
        longitude=longitude,
    )

    db_session.add(place)
    db_session.commit()
    db_session.refresh(place)

    return place


def create_plant(
    db_session,
    place_id=None,
):
    plant = Plant(
        name="فیکوس",
        place_id=place_id,
        status="active",
    )

    db_session.add(plant)
    db_session.commit()
    db_session.refresh(plant)

    return plant


def create_event(
    db_session,
    plant_id,
):
    event = PlantEvent(
        plant_id=plant_id,
        event_type="watering",
        occurred_at=datetime(
            2026,
            8,
            28,
            9,
            30,
        ),
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    return event


@patch(
    "app.services.event_weather_service.get_current_weather"
)
def test_create_weather_for_event(
    mock_get_current_weather,
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

    mock_get_current_weather.return_value = WeatherData(
        temperature=23.5,
        humidity=72,
        weather_condition="partly_cloudy",
        recorded_at=datetime(
            2026,
            8,
            28,
            9,
            30,
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
    assert snapshot.weather_condition == "partly_cloudy"
    assert snapshot.source == "open-meteo"

    mock_get_current_weather.assert_called_once_with(
        latitude=37.2073,
        longitude=50.0039,
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


def test_create_weather_for_plant_without_place(
    db_session,
):
    plant = create_plant(
        db_session,
        place_id=None,
    )

    event = create_event(
        db_session,
        plant_id=plant.id,
    )

    with pytest.raises(
        ValueError,
        match=f"Plant with id {plant.id} has no place",
    ):
        create_weather_for_event(
            session=db_session,
            event_id=event.id,
        )


def test_create_weather_for_place_without_coordinates(
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
        match=f"Place with id {place.id} has no coordinates",
    ):
        create_weather_for_event(
            session=db_session,
            event_id=event.id,
        )


@patch(
    "app.services.event_weather_service.get_current_weather"
)
def test_create_weather_for_event_rejects_duplicate_snapshot(
    mock_get_current_weather,
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

    mock_get_current_weather.return_value = WeatherData(
        temperature=21.0,
        humidity=80,
        weather_condition="light_rain",
        recorded_at=datetime(
            2026,
            8,
            28,
            9,
            30,
        ),
        source="open-meteo",
    )

    create_weather_for_event(
        session=db_session,
        event_id=event.id,
    )

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

    mock_get_current_weather.assert_called_once()