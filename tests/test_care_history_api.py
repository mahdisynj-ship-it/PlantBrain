from datetime import datetime, timezone
from unittest.mock import patch

from app.database.base import Base
from tests.test_api import client, engine


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def create_place():
    response = client.post(
        "/places",
        json={
            "name": "Test Place",
            "city": "Lahijan",
            "latitude": 37.2073,
            "longitude": 50.0039,
            "timezone": "Asia/Tehran",
        },
    )

    assert response.status_code == 200

    return response.json()


def create_plant():
    place = create_place()

    response = client.post(
        "/plants",
        json={
            "name": "Test Plant",
            "place_id": place["id"],
        },
    )

    assert response.status_code == 200

    return response.json()


def create_event(
    plant_id: int,
    event_type: str,
    occurred_at: str,
):
    response = client.post(
        f"/plants/{plant_id}/events",
        json={
            "event_type": event_type,
            "occurred_at": occurred_at,
        },
    )

    assert response.status_code == 200

    return response.json()


@patch(
    "app.services.care_history_service.datetime"
)
def test_care_history_api_with_multiple_event_types(
    mock_datetime,
):
    mock_datetime.now.return_value = datetime(
        2026,
        8,
        28,
        12,
        0,
        tzinfo=timezone.utc,
    )

    plant = create_plant()

    create_event(
        plant_id=plant["id"],
        event_type="watering",
        occurred_at="2026-08-10T09:30:00",
    )

    create_event(
        plant_id=plant["id"],
        event_type="watering",
        occurred_at="2026-08-15T09:30:00",
    )

    create_event(
        plant_id=plant["id"],
        event_type="watering",
        occurred_at="2026-08-25T09:30:00",
    )

    create_event(
        plant_id=plant["id"],
        event_type="fertilizing",
        occurred_at="2026-08-20T09:30:00",
    )

    response = client.get(
        f"/plants/{plant['id']}/care-history"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["plant_id"] == plant["id"]
    assert data["period_days"] == 30
    assert data["total_events"] == 4

    watering = data["event_types"]["watering"]

    assert watering["count"] == 3
    assert (
        watering["last_at"]
        == "2026-08-25T06:00:00"
    )
    assert (
        watering["average_interval_days"]
        == 7.5
    )
    assert (
        watering["min_interval_days"]
        == 5.0
    )
    assert (
        watering["max_interval_days"]
        == 10.0
    )

    fertilizing = data["event_types"][
        "fertilizing"
    ]

    assert fertilizing["count"] == 1
    assert (
        fertilizing["last_at"]
        == "2026-08-20T06:00:00"
    )
    assert (
        fertilizing["average_interval_days"]
        is None
    )
    assert (
        fertilizing["min_interval_days"]
        is None
    )
    assert (
        fertilizing["max_interval_days"]
        is None
    )


@patch(
    "app.services.care_history_service.datetime"
)
def test_care_history_api_period_filter(
    mock_datetime,
):
    mock_datetime.now.return_value = datetime(
        2026,
        8,
        28,
        12,
        0,
        tzinfo=timezone.utc,
    )

    plant = create_plant()

    create_event(
        plant_id=plant["id"],
        event_type="watering",
        occurred_at="2026-08-01T09:30:00",
    )

    create_event(
        plant_id=plant["id"],
        event_type="watering",
        occurred_at="2026-08-25T09:30:00",
    )

    response = client.get(
        (
            f"/plants/{plant['id']}/care-history"
            "?period_days=7"
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert data["period_days"] == 7
    assert data["total_events"] == 1
    assert (
        data["event_types"]["watering"]["count"]
        == 1
    )


def test_care_history_api_missing_plant():
    response = client.get(
        "/plants/999/care-history"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Plant with id 999 not found",
    }


def test_care_history_api_invalid_period():
    plant = create_plant()

    response = client.get(
        (
            f"/plants/{plant['id']}/care-history"
            "?period_days=0"
        )
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": (
            "period_days must be greater than 0"
        ),
    }