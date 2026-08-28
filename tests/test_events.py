from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.plant import CreatePlant
from app.schemas.plant_event import CreatePlantEvent, UpdatePlantEvent
from app.services.event_service import (
    create_event,
    get_event_by_id,
    get_plant_events,
    update_event,
)
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


def test_create_event_schema():
    data = CreatePlantEvent(
        event_type="watering",
        occurred_at=datetime(2026, 8, 18, 10, 0),
        amount=500,
        unit="ml",
        notes="آبیاری تست",
    )

    assert data.event_type == "watering"
    assert data.amount == 500
    assert data.unit == "ml"
    assert data.notes == "آبیاری تست"


def test_create_event_rejects_empty_event_type():
    with pytest.raises(ValidationError):
        CreatePlantEvent(
            event_type="",
            occurred_at=datetime(2026, 8, 18, 10, 0),
            amount=500,
            unit="ml",
        )


def test_create_event_rejects_whitespace_only_event_type():
    with pytest.raises(ValidationError):
        CreatePlantEvent(
            event_type="   ",
            occurred_at=datetime(2026, 8, 18, 10, 0),
            amount=500,
            unit="ml",
        )


def test_create_event_rejects_negative_amount():
    with pytest.raises(ValidationError):
        CreatePlantEvent(
            event_type="watering",
            occurred_at=datetime(2026, 8, 18, 10, 0),
            amount=-500,
            unit="ml",
        )


def test_create_event_service(db_session):
    plant = create_test_plant(db_session)

    data = CreatePlantEvent(
        event_type="watering",
        occurred_at=datetime(2026, 8, 18, 10, 0),
        amount=500,
        unit="ml",
        notes="آبیاری تست",
    )

    event = create_event(
        session=db_session,
        plant_id=plant.id,
        data=data,
    )

    assert event.id is not None
    assert event.plant_id == plant.id
    assert event.event_type == "watering"
    assert event.amount == 500
    assert event.unit == "ml"
    assert event.notes == "آبیاری تست"


def test_create_event_for_missing_plant(db_session):
    data = CreatePlantEvent(
        event_type="watering",
        occurred_at=datetime(2026, 8, 18, 10, 0),
        amount=500,
        unit="ml",
    )

    with pytest.raises(
        ValueError,
        match="Plant with id 999 not found",
    ):
        create_event(
            session=db_session,
            plant_id=999,
            data=data,
        )


def test_get_event_by_id(db_session):
    plant = create_test_plant(db_session)

    event = create_event(
        session=db_session,
        plant_id=plant.id,
        data=CreatePlantEvent(
            event_type="watering",
            occurred_at=datetime(2026, 8, 18, 10, 0),
            amount=500,
            unit="ml",
        ),
    )

    result = get_event_by_id(
        session=db_session,
        event_id=event.id,
    )

    assert result is not None
    assert result.id == event.id
    assert result.plant_id == plant.id


def test_get_event_by_id_returns_none_for_missing_event(db_session):
    result = get_event_by_id(
        session=db_session,
        event_id=999,
    )

    assert result is None


def test_get_plant_events(db_session):
    plant = create_test_plant(db_session)

    first = create_event(
        session=db_session,
        plant_id=plant.id,
        data=CreatePlantEvent(
            event_type="watering",
            occurred_at=datetime(2026, 8, 18, 10, 0),
            amount=500,
            unit="ml",
        ),
    )

    second = create_event(
        session=db_session,
        plant_id=plant.id,
        data=CreatePlantEvent(
            event_type="fertilizing",
            occurred_at=datetime(2026, 8, 19, 10, 0),
            amount=50,
            unit="ml",
        ),
    )

    events = get_plant_events(
        session=db_session,
        plant_id=plant.id,
    )

    assert len(events) == 2
    assert events[0].id == second.id
    assert events[1].id == first.id


def test_update_event(db_session):
    plant = create_test_plant(db_session)

    event = create_event(
        session=db_session,
        plant_id=plant.id,
        data=CreatePlantEvent(
            event_type="watering",
            occurred_at=datetime(2026, 8, 18, 10, 0),
            amount=500,
            unit="ml",
            notes="قبل از ویرایش",
        ),
    )

    data = UpdatePlantEvent(
        amount=300,
        notes="بعد از ویرایش",
    )

    updated = update_event(
        session=db_session,
        event_id=event.id,
        data=data,
    )

    assert updated is not None
    assert updated.id == event.id
    assert updated.amount == 300
    assert updated.notes == "بعد از ویرایش"
    assert updated.event_type == "watering"


def test_update_event_returns_none_for_missing_event(db_session):
    data = UpdatePlantEvent(
        amount=300,
    )

    result = update_event(
        session=db_session,
        event_id=999,
        data=data,
    )

    assert result is None

def test_create_event_converts_place_local_time_to_utc(
    db_session,
):
    from app.database.models import Place

    place = Place(
        name="Tehran Home",
        city="Tehran",
        latitude=35.6892,
        longitude=51.3890,
        timezone="Asia/Tehran",
    )

    db_session.add(place)
    db_session.commit()
    db_session.refresh(place)

    plant = create_plant(
        session=db_session,
        data=CreatePlant(
            name="Timezone Test Plant",
            place_id=place.id,
        ),
    )

    event = create_event(
        session=db_session,
        plant_id=plant.id,
        data=CreatePlantEvent(
            event_type="watering",
            occurred_at=datetime(
                2026,
                8,
                18,
                10,
                0,
            ),
        ),
    )

    assert event.occurred_at == datetime(
        2026,
        8,
        18,
        6,
        30,
    )


def test_update_event_converts_place_local_time_to_utc(
    db_session,
):
    from app.database.models import Place

    place = Place(
        name="Tehran Home",
        city="Tehran",
        latitude=35.6892,
        longitude=51.3890,
        timezone="Asia/Tehran",
    )

    db_session.add(place)
    db_session.commit()
    db_session.refresh(place)

    plant = create_plant(
        session=db_session,
        data=CreatePlant(
            name="Timezone Test Plant",
            place_id=place.id,
        ),
    )

    event = create_event(
        session=db_session,
        plant_id=plant.id,
        data=CreatePlantEvent(
            event_type="watering",
            occurred_at=datetime(
                2026,
                8,
                18,
                10,
                0,
            ),
        ),
    )

    updated = update_event(
        session=db_session,
        event_id=event.id,
        data=UpdatePlantEvent(
            occurred_at=datetime(
                2026,
                8,
                19,
                10,
                0,
            ),
        ),
    )

    assert updated is not None

    assert updated.occurred_at == datetime(
        2026,
        8,
        19,
        6,
        30,
    )
