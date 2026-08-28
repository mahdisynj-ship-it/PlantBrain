from app.database.base import Base
from tests.test_api import client, engine


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def create_plant():
    response = client.post(
        "/plants",
        json={
            "name": "فیکوس",
        },
    )

    assert response.status_code == 200

    return response.json()


def create_event(
    plant_id,
    event_type,
    occurred_at,
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


def test_watering_analysis_api_with_no_events():
    plant = create_plant()

    response = client.get(
        f"/plants/{plant['id']}/analysis/watering",
    )

    assert response.status_code == 200

    assert response.json() == {
        "plant_id": plant["id"],
        "total_events": 0,
        "last_watered_at": None,
        "average_interval_days": None,
    }


def test_watering_analysis_api_with_events():
    plant = create_plant()

    create_event(
        plant_id=plant["id"],
        event_type="watering",
        occurred_at="2026-08-01T09:00:00",
    )

    create_event(
        plant_id=plant["id"],
        event_type="fertilizing",
        occurred_at="2026-08-03T09:00:00",
    )

    create_event(
        plant_id=plant["id"],
        event_type="watering",
        occurred_at="2026-08-05T09:00:00",
    )

    create_event(
        plant_id=plant["id"],
        event_type="watering",
        occurred_at="2026-08-11T09:00:00",
    )

    response = client.get(
        f"/plants/{plant['id']}/analysis/watering",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["plant_id"] == plant["id"]
    assert data["total_events"] == 3
    assert data["last_watered_at"] == "2026-08-11T09:00:00"
    assert data["average_interval_days"] == 5.0


def test_watering_analysis_api_missing_plant():
    response = client.get(
        "/plants/999/analysis/watering",
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Plant with id 999 not found",
    }