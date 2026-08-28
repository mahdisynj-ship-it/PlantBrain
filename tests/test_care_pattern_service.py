from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.models import Plant, PlantEvent
from app.services.care_pattern_service import (
    get_care_pattern,
)
from tests.test_api import engine


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def create_plant(
    session,
) -> Plant:
    plant = Plant(
        name="Test Plant",
    )

    session.add(plant)
    session.commit()
    session.refresh(plant)

    return plant


def create_event(
    session,
    plant_id: int,
    event_type: str,
    occurred_at: datetime,
) -> PlantEvent:
    event = PlantEvent(
        plant_id=plant_id,
        event_type=event_type,
        occurred_at=occurred_at,
    )

    session.add(event)
    session.commit()
    session.refresh(event)

    return event


@patch(
    "app.services.care_pattern_service.datetime"
)
def test_regular_stable_pattern(
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

    session = TestingSessionLocal()

    try:
        plant = create_plant(
            session,
        )

        event_dates = [
            datetime(2026, 8, 1, 6, 0),
            datetime(2026, 8, 6, 6, 0),
            datetime(2026, 8, 11, 6, 0),
            datetime(2026, 8, 16, 6, 0),
            datetime(2026, 8, 21, 6, 0),
        ]

        for occurred_at in event_dates:
            create_event(
                session=session,
                plant_id=plant.id,
                event_type="watering",
                occurred_at=occurred_at,
            )

        pattern = get_care_pattern(
            session=session,
            plant_id=plant.id,
            period_days=90,
        )

        watering = pattern.event_types[
            "watering"
        ]

        assert watering.event_count == 5
        assert watering.interval_count == 4
        assert (
            watering.average_interval_days
            == 5.0
        )
        assert (
            watering.interval_std_dev_days
            == 0.0
        )
        assert watering.regularity == "regular"
        assert watering.trend == "stable"

    finally:
        session.close()


@patch(
    "app.services.care_pattern_service.datetime"
)
def test_increasing_interval_pattern(
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

    session = TestingSessionLocal()

    try:
        plant = create_plant(
            session,
        )

        event_dates = [
            datetime(2026, 8, 1, 6, 0),
            datetime(2026, 8, 4, 6, 0),
            datetime(2026, 8, 8, 6, 0),
            datetime(2026, 8, 14, 6, 0),
            datetime(2026, 8, 22, 6, 0),
        ]

        for occurred_at in event_dates:
            create_event(
                session=session,
                plant_id=plant.id,
                event_type="watering",
                occurred_at=occurred_at,
            )

        pattern = get_care_pattern(
            session=session,
            plant_id=plant.id,
        )

        watering = pattern.event_types[
            "watering"
        ]

        assert (
            watering.trend
            == "increasing_interval"
        )

    finally:
        session.close()


@patch(
    "app.services.care_pattern_service.datetime"
)
def test_decreasing_interval_pattern(
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

    session = TestingSessionLocal()

    try:
        plant = create_plant(
            session,
        )

        event_dates = [
            datetime(2026, 8, 1, 6, 0),
            datetime(2026, 8, 9, 6, 0),
            datetime(2026, 8, 15, 6, 0),
            datetime(2026, 8, 19, 6, 0),
            datetime(2026, 8, 22, 6, 0),
        ]

        for occurred_at in event_dates:
            create_event(
                session=session,
                plant_id=plant.id,
                event_type="watering",
                occurred_at=occurred_at,
            )

        pattern = get_care_pattern(
            session=session,
            plant_id=plant.id,
        )

        watering = pattern.event_types[
            "watering"
        ]

        assert (
            watering.trend
            == "decreasing_interval"
        )

    finally:
        session.close()


@patch(
    "app.services.care_pattern_service.datetime"
)
def test_irregular_pattern(
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

    session = TestingSessionLocal()

    try:
        plant = create_plant(
            session,
        )

        event_dates = [
            datetime(2026, 8, 1, 6, 0),
            datetime(2026, 8, 2, 6, 0),
            datetime(2026, 8, 12, 6, 0),
            datetime(2026, 8, 14, 6, 0),
            datetime(2026, 8, 25, 6, 0),
        ]

        for occurred_at in event_dates:
            create_event(
                session=session,
                plant_id=plant.id,
                event_type="watering",
                occurred_at=occurred_at,
            )

        pattern = get_care_pattern(
            session=session,
            plant_id=plant.id,
        )

        watering = pattern.event_types[
            "watering"
        ]

        assert watering.regularity == "irregular"

    finally:
        session.close()


@patch(
    "app.services.care_pattern_service.datetime"
)
def test_single_event_has_insufficient_data(
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

    session = TestingSessionLocal()

    try:
        plant = create_plant(
            session,
        )

        create_event(
            session=session,
            plant_id=plant.id,
            event_type="fertilizing",
            occurred_at=datetime(
                2026,
                8,
                20,
                6,
                0,
            ),
        )

        pattern = get_care_pattern(
            session=session,
            plant_id=plant.id,
        )

        fertilizing = pattern.event_types[
            "fertilizing"
        ]

        assert fertilizing.event_count == 1
        assert fertilizing.interval_count == 0

        assert (
            fertilizing.average_interval_days
            is None
        )

        assert (
            fertilizing.interval_std_dev_days
            is None
        )

        assert (
            fertilizing.regularity
            == "insufficient_data"
        )

        assert (
            fertilizing.trend
            == "insufficient_data"
        )

    finally:
        session.close()


@patch(
    "app.services.care_pattern_service.datetime"
)
def test_pattern_excludes_events_outside_period(
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

    session = TestingSessionLocal()

    try:
        plant = create_plant(
            session,
        )

        create_event(
            session=session,
            plant_id=plant.id,
            event_type="watering",
            occurred_at=datetime(
                2026,
                5,
                1,
                6,
                0,
            ),
        )

        create_event(
            session=session,
            plant_id=plant.id,
            event_type="watering",
            occurred_at=datetime(
                2026,
                8,
                20,
                6,
                0,
            ),
        )

        create_event(
            session=session,
            plant_id=plant.id,
            event_type="watering",
            occurred_at=datetime(
                2026,
                8,
                29,
                6,
                0,
            ),
        )

        pattern = get_care_pattern(
            session=session,
            plant_id=plant.id,
            period_days=30,
        )

        assert pattern.total_events == 1

        assert (
            pattern.event_types[
                "watering"
            ].event_count
            == 1
        )

    finally:
        session.close()


def test_pattern_missing_plant():
    session = TestingSessionLocal()

    try:
        with pytest.raises(
            ValueError,
            match="Plant with id 999 not found",
        ):
            get_care_pattern(
                session=session,
                plant_id=999,
            )

    finally:
        session.close()


def test_pattern_rejects_invalid_period():
    session = TestingSessionLocal()

    try:
        plant = create_plant(
            session,
        )

        with pytest.raises(
            ValueError,
            match=(
                "period_days must be greater than 0"
            ),
        ):
            get_care_pattern(
                session=session,
                plant_id=plant.id,
                period_days=0,
            )

    finally:
        session.close()