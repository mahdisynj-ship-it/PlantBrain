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
    "app.services.care_pattern_service.datetime"
)
def test_care_pattern_api_regular_stable(
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

    event_dates = [
        "2026-08-01T09:30:00",
        "2026-08-06T09:30:00",
        "2026-08-11T09:30:00",
        "2026-08-16T09:30:00",
        "2026-08-21T09:30:00",
    ]

    for occurred_at in event_dates:
        create_event(
            plant_id=plant["id"],
            event_type="watering",
            occurred_at=occurred_at,
        )

    response = client.get(
        f"/plants/{plant['id']}/care-pattern"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["plant_id"] == plant["id"]
    assert data["period_days"] == 90
    assert data["total_events"] == 5

    watering = data["event_types"][
        "watering"
    ]

    assert watering["event_count"] == 5
    assert watering["interval_count"] == 4
    assert (
        watering["average_interval_days"]
        == 5.0
    )
    assert (
        watering["interval_std_dev_days"]
        == 0.0
    )
    assert watering["regularity"] == "regular"
    assert watering["trend"] == "stable"


@patch(
    "app.services.care_pattern_service.datetime"
)
def test_care_pattern_api_increasing_interval(
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

    event_dates = [
        "2026-08-01T09:30:00",
        "2026-08-04T09:30:00",
        "2026-08-08T09:30:00",
        "2026-08-14T09:30:00",
        "2026-08-22T09:30:00",
    ]

    for occurred_at in event_dates:
        create_event(
            plant_id=plant["id"],
            event_type="watering",
            occurred_at=occurred_at,
        )

    response = client.get(
        f"/plants/{plant['id']}/care-pattern"
    )

    assert response.status_code == 200

    data = response.json()

    watering = data["event_types"][
        "watering"
    ]

    assert (
        watering["trend"]
        == "increasing_interval"
    )


@patch(
    "app.services.care_pattern_service.datetime"
)
def test_care_pattern_api_custom_period(
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
        occurred_at="2026-07-01T09:30:00",
    )

    create_event(
        plant_id=plant["id"],
        event_type="watering",
        occurred_at="2026-08-20T09:30:00",
    )

    response = client.get(
        (
            f"/plants/{plant['id']}/care-pattern"
            "?period_days=30"
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert data["period_days"] == 30
    assert data["total_events"] == 1

    watering = data["event_types"][
        "watering"
    ]

    assert watering["event_count"] == 1
    assert (
        watering["regularity"]
        == "insufficient_data"
    )
    assert (
        watering["trend"]
        == "insufficient_data"
    )


def test_care_pattern_api_missing_plant():
    response = client.get(
        "/plants/999/care-pattern"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Plant with id 999 not found",
    }


def test_care_pattern_api_invalid_period():
    plant = create_plant()

    response = client.get(
        (
            f"/plants/{plant['id']}/care-pattern"
            "?period_days=0"
        )
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": (
            "period_days must be greater than 0"
        ),
    }