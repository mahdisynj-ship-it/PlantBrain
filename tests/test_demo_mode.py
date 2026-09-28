from fastapi.testclient import TestClient

from app.api import main


client = TestClient(main.app)


def test_demo_mode_allows_get_requests(monkeypatch):
    monkeypatch.setattr(
        main,
        "DEMO_MODE",
        True,
    )

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
    }


def test_demo_mode_blocks_post_requests(monkeypatch):
    monkeypatch.setattr(
        main,
        "DEMO_MODE",
        True,
    )

    response = client.post(
        "/plants",
        json={
            "name": "Blocked Demo Plant",
        },
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": (
            "PlantBrain public demo is read-only. "
            "Data modifications are disabled."
        )
    }


def test_demo_mode_blocks_patch_requests(monkeypatch):
    monkeypatch.setattr(
        main,
        "DEMO_MODE",
        True,
    )

    response = client.patch(
        "/plants/1",
        json={
            "name": "Blocked Update",
        },
    )

    assert response.status_code == 403


def test_demo_mode_blocks_delete_requests(monkeypatch):
    monkeypatch.setattr(
        main,
        "DEMO_MODE",
        True,
    )

    response = client.delete("/plants/1")

    assert response.status_code == 403


def test_normal_mode_allows_request_to_reach_application(monkeypatch):
    monkeypatch.setattr(
        main,
        "DEMO_MODE",
        False,
    )

    response = client.post(
        "/this-route-does-not-exist",
    )

    assert response.status_code == 404
    assert response.status_code != 403