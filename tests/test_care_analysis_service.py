from datetime import datetime, timezone
from unittest.mock import patch

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
    assert result.days_since_last_watering is None
    assert result.expected_next_watering_at is None
    assert result.watering_status == "unknown"


@patch(
    "app.services.care_analysis_service.datetime"
)
def test_analyze_watering_with_one_event(
    mock_datetime,
    db_session,
):
    mock_datetime.now.return_value = datetime(
        2026,
        8,
        28,
        5,
        30,
        tzinfo=timezone.utc,
    )

    occurred_at = datetime(
        2026,
        8,
        20,
        9,
        0,
    )

    plant = create_plant(
        db_session,
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
    assert result.days_since_last_watering == 8.0
    assert result.expected_next_watering_at is None
    assert result.watering_status == "unknown"


@patch(
    "app.services.care_analysis_service.datetime"
)
def test_analyze_watering_not_due(
    mock_datetime,
    db_session,
):
    mock_datetime.now.return_value = datetime(
        2026,
        8,
        18,
        5,
        30,
        tzinfo=timezone.utc,
    )

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
            11,
            9,
            0,
        ),
    )

    result = analyze_watering(
        session=db_session,
        plant_id=plant.id,
    )

    assert result.total_events == 2
    assert result.average_interval_days == 10.0

    assert result.expected_next_watering_at == datetime(
        2026,
        8,
        21,
        9,
        0,
    )

    assert result.days_since_last_watering == 7.0
    assert result.watering_status == "not_due"


@patch(
    "app.services.care_analysis_service.datetime"
)
def test_analyze_watering_due(
    mock_datetime,
    db_session,
):
    mock_datetime.now.return_value = datetime(
        2026,
        8,
        21,
        5,
        30,
        tzinfo=timezone.utc,
    )

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
            11,
            9,
            0,
        ),
    )

    result = analyze_watering(
        session=db_session,
        plant_id=plant.id,
    )

    assert result.days_since_last_watering == 10.0
    assert result.watering_status == "due"


@patch(
    "app.services.care_analysis_service.datetime"
)
def test_analyze_watering_overdue(
    mock_datetime,
    db_session,
):
    mock_datetime.now.return_value = datetime(
        2026,
        8,
        25,
        5,
        30,
        tzinfo=timezone.utc,
    )

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
            11,
            9,
            0,
        ),
    )

    result = analyze_watering(
        session=db_session,
        plant_id=plant.id,
    )

    assert result.days_since_last_watering == 14.0
    assert result.watering_status == "overdue"


@patch(
    "app.services.care_analysis_service.datetime"
)
def test_analyze_watering_with_multiple_intervals(
    mock_datetime,
    db_session,
):
    mock_datetime.now.return_value = datetime(
        2026,
        8,
        15,
        5,
        30,
        tzinfo=timezone.utc,
    )

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
    assert result.average_interval_days == 5.0

    assert result.last_watered_at == datetime(
        2026,
        8,
        11,
        9,
        0,
    )

    assert result.expected_next_watering_at == datetime(
        2026,
        8,
        16,
        9,
        0,
    )

    assert result.days_since_last_watering == 4.0
    assert result.watering_status == "due"


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