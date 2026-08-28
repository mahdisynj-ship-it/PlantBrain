from app.database.base import Base

from tests.test_api import client, engine


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def create_place_payload(
    name="خانه",
    city="لاهیجان",
    latitude=37.2073,
    longitude=50.0039,
):
    return {
        "name": name,
        "city": city,
        "latitude": latitude,
        "longitude": longitude,
    }


def create_plant_payload(
    name="فیکوس",
    place_id=None,
):
    payload = {
        "name": name,
    }

    if place_id is not None:
        payload["place_id"] = place_id

    return payload


def test_create_place_api():
    response = client.post(
        "/places",
        json=create_place_payload(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] is not None
    assert data["name"] == "خانه"
    assert data["city"] == "لاهیجان"
    assert data["latitude"] == 37.2073
    assert data["longitude"] == 50.0039


def test_get_places_api():
    first_response = client.post(
        "/places",
        json=create_place_payload(
            name="خانه",
        ),
    )

    second_response = client.post(
        "/places",
        json=create_place_payload(
            name="دفتر",
        ),
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    response = client.get(
        "/places",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "دفتر"
    assert data[1]["name"] == "خانه"


def test_get_place_by_id_api():
    create_response = client.post(
        "/places",
        json=create_place_payload(),
    )

    place_id = create_response.json()["id"]

    response = client.get(
        f"/places/{place_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == place_id
    assert data["name"] == "خانه"


def test_get_missing_place_api():
    response = client.get(
        "/places/999",
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Place with id 999 not found",
    }


def test_update_place_api():
    create_response = client.post(
        "/places",
        json=create_place_payload(
            name="خانه قدیمی",
        ),
    )

    place_id = create_response.json()["id"]

    response = client.patch(
        f"/places/{place_id}",
        json={
            "name": "خانه جدید",
            "city": "رشت",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == place_id
    assert data["name"] == "خانه جدید"
    assert data["city"] == "رشت"


def test_update_missing_place_api():
    response = client.patch(
        "/places/999",
        json={
            "name": "خانه",
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Place with id 999 not found",
    }


def test_delete_place_api():
    create_response = client.post(
        "/places",
        json=create_place_payload(),
    )

    place_id = create_response.json()["id"]

    response = client.delete(
        f"/places/{place_id}",
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": "Place deleted successfully",
        "place_id": place_id,
    }

    get_response = client.get(
        f"/places/{place_id}",
    )

    assert get_response.status_code == 404


def test_delete_missing_place_api():
    response = client.delete(
        "/places/999",
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Place with id 999 not found",
    }


def test_create_plant_with_place_api():
    place_response = client.post(
        "/places",
        json=create_place_payload(),
    )

    place_id = place_response.json()["id"]

    plant_response = client.post(
        "/plants",
        json=create_plant_payload(
            place_id=place_id,
        ),
    )

    assert plant_response.status_code == 200

    data = plant_response.json()

    assert data["name"] == "فیکوس"
    assert data["place_id"] == place_id


def test_create_plant_with_missing_place_api():
    response = client.post(
        "/plants",
        json=create_plant_payload(
            place_id=999,
        ),
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Place with id 999 not found",
    }


def test_update_plant_place_api():
    first_place_response = client.post(
        "/places",
        json=create_place_payload(
            name="خانه",
        ),
    )

    second_place_response = client.post(
        "/places",
        json=create_place_payload(
            name="دفتر",
        ),
    )

    first_place_id = first_place_response.json()["id"]
    second_place_id = second_place_response.json()["id"]

    plant_response = client.post(
        "/plants",
        json=create_plant_payload(
            place_id=first_place_id,
        ),
    )

    plant_id = plant_response.json()["id"]

    response = client.patch(
        f"/plants/{plant_id}",
        json={
            "place_id": second_place_id,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["place_id"] == second_place_id


def test_update_plant_with_missing_place_api():
    plant_response = client.post(
        "/plants",
        json=create_plant_payload(),
    )

    plant_id = plant_response.json()["id"]

    response = client.patch(
        f"/plants/{plant_id}",
        json={
            "place_id": 999,
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Place with id 999 not found",
    }


def test_remove_place_from_plant_api():
    place_response = client.post(
        "/places",
        json=create_place_payload(),
    )

    place_id = place_response.json()["id"]

    plant_response = client.post(
        "/plants",
        json=create_plant_payload(
            place_id=place_id,
        ),
    )

    plant_id = plant_response.json()["id"]

    response = client.patch(
        f"/plants/{plant_id}",
        json={
            "place_id": None,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["place_id"] is None


def test_delete_place_sets_plant_place_id_to_none():
    place_response = client.post(
        "/places",
        json=create_place_payload(),
    )

    place_id = place_response.json()["id"]

    plant_response = client.post(
        "/plants",
        json=create_plant_payload(
            place_id=place_id,
        ),
    )

    plant_id = plant_response.json()["id"]

    delete_response = client.delete(
        f"/places/{place_id}",
    )

    assert delete_response.status_code == 200

    plant_response = client.get(
        f"/plants/{plant_id}",
    )

    assert plant_response.status_code == 200

    data = plant_response.json()

    assert data["id"] == plant_id
    assert data["name"] == "فیکوس"
    assert data["place_id"] is None