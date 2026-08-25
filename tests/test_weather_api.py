from tests.test_api import (
    client,
    create_event_payload,
    create_plant_payload,
    engine,
)

from app.database.base import Base


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def create_weather_payload():
    return {
        "temperature": 26.5,
        "humidity": 70,
        "weather_condition": "partly_cloudy",
        "recorded_at": "2026-08-25T10:00:00",
        "source": "test",
    }


def create_test_event():
    plant_response = client.post(
        "/plants",
        json=create_plant_payload(),
    )

    assert plant_response.status_code == 200

    plant_id = plant_response.json()["id"]

    event_response = client.post(
        f"/plants/{plant_id}/events",
        json=create_event_payload(),
    )

    assert event_response.status_code == 200

    return event_response.json()["id"]


def test_create_weather_snapshot():
    event_id = create_test_event()

    response = client.post(
        f"/plant-events/{event_id}/weather",
        json=create_weather_payload(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["event_id"] == event_id
    assert data["temperature"] == 26.5
    assert data["humidity"] == 70
    assert data["weather_condition"] == "partly_cloudy"
    assert data["source"] == "test"


def test_create_weather_for_missing_event():
    response = client.post(
        "/plant-events/999/weather",
        json=create_weather_payload(),
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Event with id 999 not found",
    }


def test_create_duplicate_weather_snapshot():
    event_id = create_test_event()

    first_response = client.post(
        f"/plant-events/{event_id}/weather",
        json=create_weather_payload(),
    )

    assert first_response.status_code == 200

    second_response = client.post(
        f"/plant-events/{event_id}/weather",
        json=create_weather_payload(),
    )

    assert second_response.status_code == 409

    assert second_response.json() == {
        "detail": f"Weather snapshot for event id {event_id} already exists",
    }


def test_create_weather_rejects_invalid_humidity():
    event_id = create_test_event()

    payload = create_weather_payload()
    payload["humidity"] = 101

    response = client.post(
        f"/plant-events/{event_id}/weather",
        json=payload,
    )

    assert response.status_code == 422


def test_get_weather_snapshot():
    event_id = create_test_event()

    create_response = client.post(
        f"/plant-events/{event_id}/weather",
        json=create_weather_payload(),
    )

    assert create_response.status_code == 200

    response = client.get(
        f"/plant-events/{event_id}/weather",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["event_id"] == event_id
    assert data["temperature"] == 26.5
    assert data["humidity"] == 70
    assert data["weather_condition"] == "partly_cloudy"
    assert data["source"] == "test"


def test_get_missing_weather_snapshot():
    event_id = create_test_event()

    response = client.get(
        f"/plant-events/{event_id}/weather",
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": f"Weather snapshot for event id {event_id} not found",
    }


def test_update_weather_snapshot():
    event_id = create_test_event()

    create_response = client.post(
        f"/plant-events/{event_id}/weather",
        json=create_weather_payload(),
    )

    assert create_response.status_code == 200

    response = client.patch(
        f"/plant-events/{event_id}/weather",
        json={
            "temperature": 28,
            "humidity": 60,
            "weather_condition": "sunny",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["event_id"] == event_id
    assert data["temperature"] == 28
    assert data["humidity"] == 60
    assert data["weather_condition"] == "sunny"
    assert data["source"] == "test"


def test_update_missing_weather_snapshot():
    event_id = create_test_event()

    response = client.patch(
        f"/plant-events/{event_id}/weather",
        json={
            "temperature": 28,
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": f"Weather snapshot for event id {event_id} not found",
    }


def test_delete_weather_snapshot():
    event_id = create_test_event()

    create_response = client.post(
        f"/plant-events/{event_id}/weather",
        json=create_weather_payload(),
    )

    assert create_response.status_code == 200

    delete_response = client.delete(
        f"/plant-events/{event_id}/weather",
    )

    assert delete_response.status_code == 200

    assert delete_response.json() == {
        "message": "Weather snapshot deleted successfully",
        "event_id": event_id,
    }

    get_response = client.get(
        f"/plant-events/{event_id}/weather",
    )

    assert get_response.status_code == 404


def test_delete_missing_weather_snapshot():
    event_id = create_test_event()

    response = client.delete(
        f"/plant-events/{event_id}/weather",
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": f"Weather snapshot for event id {event_id} not found",
    }