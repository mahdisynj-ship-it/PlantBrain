from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.place import CreatePlace
from app.schemas.plant import CreatePlant
from app.schemas.plant_event import CreatePlantEvent
from app.schemas.weather_snapshot import (
    CreateWeatherSnapshot,
    UpdateWeatherSnapshot,
)
from app.services.event_service import create_event
from app.services.place_service import create_place
from app.services.plant_service import create_plant
from app.services.weather_service import (
    create_weather_snapshot,
    delete_weather_snapshot,
    get_weather_snapshot_by_event_id,
    update_weather_snapshot,
)


def create_test_event(db_session):
    plant = create_plant(
        session=db_session,
        data=CreatePlant(
            name="فیکوس تست",
            scientific_name="Ficus elastica",
            location="اتاق تست",
        ),
    )

    return create_event(
        session=db_session,
        plant_id=plant.id,
        data=CreatePlantEvent(
            event_type="watering",
            occurred_at=datetime(
                2026,
                8,
                25,
                10,
                0,
            ),
            amount=500,
            unit="ml",
        ),
    )


def create_test_event_with_place(
    db_session,
    timezone_name: str,
):
    place = create_place(
        session=db_session,
        data=CreatePlace(
            name="Test Place",
            city="Test City",
            latitude=35.0,
            longitude=51.0,
            timezone=timezone_name,
        ),
    )

    plant = create_plant(
        session=db_session,
        data=CreatePlant(
            name="Timezone Test Plant",
            place_id=place.id,
        ),
    )

    return create_event(
        session=db_session,
        plant_id=plant.id,
        data=CreatePlantEvent(
            event_type="watering",
            occurred_at=datetime(
                2026,
                8,
                25,
                10,
                0,
            ),
        ),
    )


def test_create_weather_snapshot_schema():
    data = CreateWeatherSnapshot(
        temperature=26.5,
        humidity=70,
        weather_condition="partly_cloudy",
        recorded_at=datetime(
            2026,
            8,
            25,
            10,
            0,
        ),
        source="test",
    )

    assert data.temperature == 26.5
    assert data.humidity == 70
    assert (
        data.weather_condition
        == "partly_cloudy"
    )
    assert data.source == "test"


def test_weather_snapshot_rejects_humidity_above_100():
    with pytest.raises(
        ValidationError,
    ):
        CreateWeatherSnapshot(
            temperature=26,
            humidity=101,
            recorded_at=datetime(
                2026,
                8,
                25,
                10,
                0,
            ),
        )


def test_weather_snapshot_rejects_negative_humidity():
    with pytest.raises(
        ValidationError,
    ):
        CreateWeatherSnapshot(
            temperature=26,
            humidity=-1,
            recorded_at=datetime(
                2026,
                8,
                25,
                10,
                0,
            ),
        )


def test_create_weather_snapshot(
    db_session,
):
    event = create_test_event(
        db_session,
    )

    snapshot = create_weather_snapshot(
        session=db_session,
        event_id=event.id,
        data=CreateWeatherSnapshot(
            temperature=26.5,
            humidity=70,
            weather_condition=(
                "partly_cloudy"
            ),
            recorded_at=datetime(
                2026,
                8,
                25,
                10,
                0,
            ),
            source="test",
        ),
    )

    assert snapshot.id is not None
    assert snapshot.event_id == event.id
    assert snapshot.temperature == 26.5
    assert snapshot.humidity == 70
    assert (
        snapshot.weather_condition
        == "partly_cloudy"
    )
    assert snapshot.source == "test"


def test_create_weather_snapshot_for_missing_event(
    db_session,
):
    data = CreateWeatherSnapshot(
        temperature=26,
        humidity=70,
        recorded_at=datetime(
            2026,
            8,
            25,
            10,
            0,
        ),
    )

    with pytest.raises(
        ValueError,
        match="Event with id 999 not found",
    ):
        create_weather_snapshot(
            session=db_session,
            event_id=999,
            data=data,
        )


def test_event_cannot_have_two_weather_snapshots(
    db_session,
):
    event = create_test_event(
        db_session,
    )

    data = CreateWeatherSnapshot(
        temperature=26,
        humidity=70,
        recorded_at=datetime(
            2026,
            8,
            25,
            10,
            0,
        ),
    )

    create_weather_snapshot(
        session=db_session,
        event_id=event.id,
        data=data,
    )

    with pytest.raises(
        ValueError,
        match=(
            f"Weather snapshot for event id "
            f"{event.id} already exists"
        ),
    ):
        create_weather_snapshot(
            session=db_session,
            event_id=event.id,
            data=data,
        )


def test_get_weather_snapshot_by_event_id(
    db_session,
):
    event = create_test_event(
        db_session,
    )

    snapshot = create_weather_snapshot(
        session=db_session,
        event_id=event.id,
        data=CreateWeatherSnapshot(
            temperature=25,
            humidity=65,
            recorded_at=datetime(
                2026,
                8,
                25,
                10,
                0,
            ),
        ),
    )

    result = (
        get_weather_snapshot_by_event_id(
            session=db_session,
            event_id=event.id,
        )
    )

    assert result is not None
    assert result.id == snapshot.id
    assert result.event_id == event.id


def test_get_weather_snapshot_returns_none_when_missing(
    db_session,
):
    result = (
        get_weather_snapshot_by_event_id(
            session=db_session,
            event_id=999,
        )
    )

    assert result is None


def test_update_weather_snapshot(
    db_session,
):
    event = create_test_event(
        db_session,
    )

    snapshot = create_weather_snapshot(
        session=db_session,
        event_id=event.id,
        data=CreateWeatherSnapshot(
            temperature=25,
            humidity=65,
            weather_condition="cloudy",
            recorded_at=datetime(
                2026,
                8,
                25,
                10,
                0,
            ),
        ),
    )

    updated = update_weather_snapshot(
        session=db_session,
        event_id=event.id,
        data=UpdateWeatherSnapshot(
            temperature=27,
            humidity=60,
            weather_condition="sunny",
        ),
    )

    assert updated is not None
    assert updated.id == snapshot.id
    assert updated.temperature == 27
    assert updated.humidity == 60
    assert (
        updated.weather_condition
        == "sunny"
    )


def test_update_missing_weather_snapshot(
    db_session,
):
    result = update_weather_snapshot(
        session=db_session,
        event_id=999,
        data=UpdateWeatherSnapshot(
            temperature=27,
        ),
    )

    assert result is None


def test_delete_weather_snapshot(
    db_session,
):
    event = create_test_event(
        db_session,
    )

    create_weather_snapshot(
        session=db_session,
        event_id=event.id,
        data=CreateWeatherSnapshot(
            temperature=25,
            humidity=65,
            recorded_at=datetime(
                2026,
                8,
                25,
                10,
                0,
            ),
        ),
    )

    deleted = delete_weather_snapshot(
        session=db_session,
        event_id=event.id,
    )

    assert deleted is True

    result = (
        get_weather_snapshot_by_event_id(
            session=db_session,
            event_id=event.id,
        )
    )

    assert result is None


def test_delete_missing_weather_snapshot(
    db_session,
):
    deleted = delete_weather_snapshot(
        session=db_session,
        event_id=999,
    )

    assert deleted is False


def test_create_weather_snapshot_stores_tehran_time_as_utc(
    db_session,
):
    event = create_test_event_with_place(
        db_session=db_session,
        timezone_name="Asia/Tehran",
    )

    snapshot = create_weather_snapshot(
        session=db_session,
        event_id=event.id,
        data=CreateWeatherSnapshot(
            temperature=26,
            humidity=70,
            recorded_at=datetime(
                2026,
                8,
                25,
                10,
                0,
            ),
            source="test",
        ),
    )

    assert snapshot.recorded_at == datetime(
        2026,
        8,
        25,
        6,
        30,
    )

    assert snapshot.recorded_at.tzinfo is None


def test_update_weather_snapshot_stores_bogota_time_as_utc(
    db_session,
):
    event = create_test_event_with_place(
        db_session=db_session,
        timezone_name="America/Bogota",
    )

    create_weather_snapshot(
        session=db_session,
        event_id=event.id,
        data=CreateWeatherSnapshot(
            temperature=26,
            humidity=70,
            recorded_at=datetime(
                2026,
                8,
                25,
                9,
                0,
            ),
            source="test",
        ),
    )

    updated = update_weather_snapshot(
        session=db_session,
        event_id=event.id,
        data=UpdateWeatherSnapshot(
            recorded_at=datetime(
                2026,
                8,
                25,
                10,
                0,
            ),
        ),
    )

    assert updated is not None

    assert updated.recorded_at == datetime(
        2026,
        8,
        25,
        15,
        0,
    )

    assert updated.recorded_at.tzinfo is None