from datetime import datetime

import pytest

from app.database.models import Plant, PlantEvent
from app.services.care_analysis_service import analyze_watering


def create_plant(
    db_session,
    name="فیکوس",
):
    plant = Plant(
        name=name,
        status="active",
    )

    db_session.add(plant)
    db_session.commit()
    db_session.refresh(plant)

    return plant


def create_event(
    db_session,
    plant_id,
    event_type,
    occurred_at,
):
    event = PlantEvent(
        plant_id=plant_id,
        event_type=event_type,
        occurred_at=occurred_at,
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    return event


def test_analyze_watering_with_no_events(
    db_session,
):
    plant = create_plant(
        db_session,
    )

    result = analyze_watering(
        session=db_session,
        plant_id=plant.id,
    )

    assert result.plant_id == plant.id
    assert result.total_events == 0
    assert result.last_watered_at is None
    assert result.average_interval_days is None


def test_analyze_watering_with_one_event(
    db_session,
):
    plant = create_plant(
        db_session,
    )

    occurred_at = datetime(
        2026,
        8,
        20,
        9,
        0,
    )

    create_event(
        db_session,
        plant_id=plant.id,
        event_type="watering",
        occurred_at=occurred_at,
    )

    result = analyze_watering(
        session=db_session,
        plant_id=plant.id,
    )

    assert result.total_events == 1
    assert result.last_watered_at == occurred_at
    assert result.average_interval_days is None


def test_analyze_watering_with_multiple_events(
    db_session,
):
    plant = create_plant(
        db_session,
    )

    create_event(
        db_session,
        plant_id=plant.id,
        event_type="watering",
        occurred_at=datetime(
            2026,
            8,
            1,
            9,
            0,
        ),
    )

    create_event(
        db_session,
        plant_id=plant.id,
        event_type="watering",
        occurred_at=datetime(
            2026,
            8,
            5,
            9,
            0,
        ),
    )

    create_event(
        db_session,
        plant_id=plant.id,
        event_type="watering",
        occurred_at=datetime(
            2026,
            8,
            11,
            9,
            0,
        ),
    )

    result = analyze_watering(
        session=db_session,
        plant_id=plant.id,
    )

    assert result.total_events == 3

    assert result.last_watered_at == datetime(
        2026,
        8,
        11,
        9,
        0,
    )

    assert result.average_interval_days == 5.0


def test_analyze_watering_ignores_other_event_types(
    db_session,
):
    plant = create_plant(
        db_session,
    )

    create_event(
        db_session,
        plant_id=plant.id,
        event_type="watering",
        occurred_at=datetime(
            2026,
            8,
            1,
            9,
            0,
        ),
    )

    create_event(
        db_session,
        plant_id=plant.id,
        event_type="fertilizing",
        occurred_at=datetime(
            2026,
            8,
            3,
            9,
            0,
        ),
    )

    create_event(
        db_session,
        plant_id=plant.id,
        event_type="watering",
        occurred_at=datetime(
            2026,
            8,
            7,
            9,
            0,
        ),
    )

    result = analyze_watering(
        session=db_session,
        plant_id=plant.id,
    )

    assert result.total_events == 2
    assert result.average_interval_days == 6.0


def test_analyze_watering_missing_plant(
    db_session,
):
    with pytest.raises(
        ValueError,
        match="Plant with id 999 not found",
    ):
        analyze_watering(
            session=db_session,
            plant_id=999,
        )