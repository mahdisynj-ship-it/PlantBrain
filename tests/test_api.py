from datetime import datetime

from fastapi.testclient import TestClient

from app.api.main import app, get_session
from app.database.base import Base
from app.database.models import Plant, PlantEvent
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)


def override_get_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)


def setup_function():
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def create_plant_payload():
    return {
        "name": "فیکوس تست API",
        "scientific_name": "Ficus elastica",
        "common_name": "Rubber Plant",
        "location": "اتاق تست",
        "status": "active",
        "notes": "تست API",
    }


def create_event_payload():
    return {
        "event_type": "watering",
        "occurred_at": "2026-08-18T10:00:00",
        "amount": 500,
        "unit": "ml",
        "notes": "آبیاری تست API",
    }


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
    }


def test_create_plant():
    response = client.post(
        "/plants",
        json=create_plant_payload(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "فیکوس تست API"
    assert data["scientific_name"] == "Ficus elastica"
    assert data["location"] == "اتاق تست"
    assert data["status"] == "active"


def test_get_plants():
    create_response = client.post(
        "/plants",
        json=create_plant_payload(),
    )

    assert create_response.status_code == 200

    response = client.get("/plants")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "فیکوس تست API"


def test_get_plant():
    create_response = client.post(
        "/plants",
        json=create_plant_payload(),
    )

    plant_id = create_response.json()["id"]

    response = client.get(f"/plants/{plant_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == plant_id
    assert data["name"] == "فیکوس تست API"


def test_get_missing_plant():
    response = client.get("/plants/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Plant with id 999 not found",
    }


def test_update_plant():
    create_response = client.post(
        "/plants",
        json=create_plant_payload(),
    )

    plant_id = create_response.json()["id"]

    response = client.patch(
        f"/plants/{plant_id}",
        json={
            "name": "فیکوس ویرایش شده",
            "location": "پذیرایی",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == plant_id
    assert data["name"] == "فیکوس ویرایش شده"
    assert data["location"] == "پذیرایی"
    assert data["status"] == "active"


def test_update_missing_plant():
    response = client.patch(
        "/plants/999",
        json={
            "name": "گیاه ناموجود",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Plant with id 999 not found",
    }


def test_delete_plant():
    create_response = client.post(
        "/plants",
        json=create_plant_payload(),
    )

    plant_id = create_response.json()["id"]

    response = client.delete(
        f"/plants/{plant_id}",
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": "Plant deleted successfully",
        "plant_id": plant_id,
    }

    get_response = client.get(
        f"/plants/{plant_id}",
    )

    assert get_response.status_code == 404


def test_delete_missing_plant():
    response = client.delete("/plants/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Plant with id 999 not found",
    }


def test_create_event():
    plant_response = client.post(
        "/plants",
        json=create_plant_payload(),
    )

    plant_id = plant_response.json()["id"]

    response = client.post(
        f"/plants/{plant_id}/events",
        json=create_event_payload(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["plant_id"] == plant_id
    assert data["event_type"] == "watering"
    assert data["amount"] == 500
    assert data["unit"] == "ml"
    assert data["notes"] == "آبیاری تست API"


def test_create_event_for_missing_plant():
    response = client.post(
        "/plants/999/events",
        json=create_event_payload(),
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Plant with id 999 not found",
    }


def test_get_plant_events():
    plant_response = client.post(
        "/plants",
        json=create_plant_payload(),
    )

    plant_id = plant_response.json()["id"]

    client.post(
        f"/plants/{plant_id}/events",
        json=create_event_payload(),
    )

    response = client.get(
        f"/plants/{plant_id}/events",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["plant_id"] == plant_id
    assert data[0]["event_type"] == "watering"


def test_get_event():
    plant_response = client.post(
        "/plants",
        json=create_plant_payload(),
    )

    plant_id = plant_response.json()["id"]

    event_response = client.post(
        f"/plants/{plant_id}/events",
        json=create_event_payload(),
    )

    event_id = event_response.json()["id"]

    response = client.get(
        f"/plant-events/{event_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == event_id
    assert data["plant_id"] == plant_id
    assert data["event_type"] == "watering"


def test_get_missing_event():
    response = client.get("/plant-events/999")

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Event with id 999 not found",
    }


def test_update_event():
    plant_response = client.post(
        "/plants",
        json=create_plant_payload(),
    )

    plant_id = plant_response.json()["id"]

    event_response = client.post(
        f"/plants/{plant_id}/events",
        json=create_event_payload(),
    )

    event_id = event_response.json()["id"]

    response = client.patch(
        f"/plant-events/{event_id}",
        json={
            "amount": 300,
            "notes": "آبیاری ویرایش شده",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == event_id
    assert data["amount"] == 300
    assert data["notes"] == "آبیاری ویرایش شده"
    assert data["event_type"] == "watering"


def test_update_missing_event():
    response = client.patch(
        "/plant-events/999",
        json={
            "amount": 300,
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Event with id 999 not found",
    }


def test_delete_event():
    plant_response = client.post(
        "/plants",
        json=create_plant_payload(),
    )

    plant_id = plant_response.json()["id"]

    event_response = client.post(
        f"/plants/{plant_id}/events",
        json=create_event_payload(),
    )

    event_id = event_response.json()["id"]

    response = client.delete(
        f"/plant-events/{event_id}",
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": "Event deleted successfully",
        "event_id": event_id,
    }

    get_response = client.get(
        f"/plant-events/{event_id}",
    )

    assert get_response.status_code == 404


def test_delete_missing_event():
    response = client.delete("/plant-events/999")

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Event with id 999 not found",
    }