from datetime import datetime
from unittest.mock import patch

from app.database.base import Base
from app.services.weather_provider import WeatherData
from tests.test_api import client, engine


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def create_place(
    name="خانه",
    latitude=37.2073,
    longitude=50.0039,
):
    response = client.post(
        "/places",
        json={
            "name": name,
            "city": "لاهیجان",
            "latitude": latitude,
            "longitude": longitude,
        },
    )

    assert response.status_code == 200

    return response.json()


def create_plant(
    place_id=None,
):
    payload = {
        "name": "فیکوس",
    }

    if place_id is not None:
        payload["place_id"] = place_id

    response = client.post(
        "/plants",
        json=payload,
    )

    assert response.status_code == 200

    return response.json()


def create_event(
    plant_id,
):
    response = client.post(
        f"/plants/{plant_id}/events",
        json={
            "event_type": "watering",
            "occurred_at": "2026-08-28T09:30:00",
        },
    )

    assert response.status_code == 200

    return response.json()


@patch(
    "app.services.event_weather_service.get_weather_for_time"
)
def test_create_automatic_weather_snapshot_api(
    mock_get_weather_for_time,
):
    place = create_place()
    plant = create_plant(
        place_id=place["id"],
    )
    event = create_event(
        plant_id=plant["id"],
    )

    mock_get_weather_for_time.return_value = WeatherData(
        temperature=24.5,
        humidity=70,
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

    response = client.post(
        f"/plant-events/{event['id']}/weather/auto",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["event_id"] == event["id"]
    assert data["temperature"] == 24.5
    assert data["humidity"] == 70
    assert data["weather_condition"] == "partly_cloudy"
    assert data["source"] == "open-meteo"

    mock_get_weather_for_time.assert_called_once_with(
        latitude=37.2073,
        longitude=50.0039,
        occurred_at=datetime(
            2026,
            8,
            28,
            9,
            30,
        ),
    )


def test_automatic_weather_missing_event_api():
    response = client.post(
        "/plant-events/999/weather/auto",
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Event with id 999 not found",
    }


def test_automatic_weather_plant_without_place_api():
    plant = create_plant()

    event = create_event(
        plant_id=plant["id"],
    )

    response = client.post(
        f"/plant-events/{event['id']}/weather/auto",
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": f"Plant with id {plant['id']} has no place",
    }


def test_automatic_weather_place_without_coordinates_api():
    place = create_place(
        latitude=None,
        longitude=None,
    )

    plant = create_plant(
        place_id=place["id"],
    )

    event = create_event(
        plant_id=plant["id"],
    )

    response = client.post(
        f"/plant-events/{event['id']}/weather/auto",
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": (
            f"Place with id {place['id']} "
            "has no coordinates"
        ),
    }


@patch(
    "app.services.event_weather_service.get_weather_for_time"
)
def test_automatic_weather_duplicate_api(
    mock_get_weather_for_time,
):
    place = create_place()

    plant = create_plant(
        place_id=place["id"],
    )

    event = create_event(
        plant_id=plant["id"],
    )

    mock_get_weather_for_time.return_value = WeatherData(
        temperature=20.0,
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

    first_response = client.post(
        f"/plant-events/{event['id']}/weather/auto",
    )

    assert first_response.status_code == 200

    second_response = client.post(
        f"/plant-events/{event['id']}/weather/auto",
    )

    assert second_response.status_code == 409

    assert second_response.json() == {
        "detail": (
            f"Weather snapshot for event id "
            f"{event['id']} already exists"
        ),
    }

    mock_get_weather_for_time.assert_called_once()