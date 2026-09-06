from datetime import datetime

from fastapi.testclient import TestClient

from app.api.main import app, get_session
from app.schemas.plant import CreatePlant
from app.schemas.plant_event import CreatePlantEvent
from app.services.event_service import create_event
from app.services.plant_service import create_plant


def create_test_plant(db_session):
    return create_plant(
        session=db_session,
        data=CreatePlant(
            name="فیکوس تست",
            scientific_name="Ficus elastica",
            location="اتاق تست",
        ),
    )


def test_get_plant_insight_api(
    db_session,
):
    def override_get_session():
        yield db_session

    app.dependency_overrides[
        get_session
    ] = override_get_session

    client = TestClient(app)

    try:
        plant = create_test_plant(
            db_session,
        )

        create_event(
            session=db_session,
            plant_id=plant.id,
            data=CreatePlantEvent(
                event_type="watering",
                occurred_at=datetime(
                    2026,
                    8,
                    1,
                    9,
                    0,
                ),
            ),
        )

        create_event(
            session=db_session,
            plant_id=plant.id,
            data=CreatePlantEvent(
                event_type="watering",
                occurred_at=datetime(
                    2026,
                    8,
                    7,
                    9,
                    0,
                ),
            ),
        )

        create_event(
            session=db_session,
            plant_id=plant.id,
            data=CreatePlantEvent(
                event_type="watering",
                occurred_at=datetime(
                    2026,
                    8,
                    13,
                    9,
                    0,
                ),
            ),
        )

        response = client.get(
            f"/plants/{plant.id}/insights"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["plant_id"] == plant.id
        assert (
            data["plant_name"]
            == "فیکوس تست"
        )

        assert "watering" in data
        assert "pattern" in data
        assert "recommendation" in data

        assert data["watering"]["status"] in [
            "not_due",
            "due",
            "overdue",
        ]

        assert (
            data["pattern"]["regularity"]
            == "regular"
        )

        assert (
            data["pattern"]["trend"]
            == "insufficient_data"
        )

        assert (
            data["recommendation"]["action"]
            in [
                "monitor",
                "water_soon",
                "water_now",
                "collect_more_data",
            ]
        )

        assert (
            data["recommendation"]["priority"]
            in [
                "low",
                "medium",
                "high",
            ]
        )

        assert isinstance(
            data["recommendation"]["message"],
            str,
        )

    finally:
        app.dependency_overrides.clear()


def test_get_plant_insight_api_missing_plant(
    db_session,
):
    def override_get_session():
        yield db_session

    app.dependency_overrides[
        get_session
    ] = override_get_session

    client = TestClient(app)

    try:
        response = client.get(
            "/plants/999/insights"
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": (
                "Plant with id 999 not found"
            ),
        }

    finally:
        app.dependency_overrides.clear()