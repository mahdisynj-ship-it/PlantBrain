from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.models import Plant, PlantEvent
from app.services.care_history_service import (
    get_care_history,
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
    "app.services.care_history_service.datetime"
)
def test_care_history_with_multiple_event_types(
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
        plant = create_plant(session)

        create_event(
            session=session,
            plant_id=plant.id,
            event_type="watering",
            occurred_at=datetime(
                2026,
                8,
                10,
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
                15,
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
                25,
                6,
                0,
            ),
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

        history = get_care_history(
            session=session,
            plant_id=plant.id,
            period_days=30,
        )

        assert history.plant_id == plant.id
        assert history.period_days == 30
        assert history.total_events == 4

        watering = history.event_types[
            "watering"
        ]

        assert watering.count == 3

        assert watering.last_at == datetime(
            2026,
            8,
            25,
            6,
            0,
        )

        assert (
            watering.average_interval_days
            == 7.5
        )

        assert (
            watering.min_interval_days
            == 5.0
        )

        assert (
            watering.max_interval_days
            == 10.0
        )

        fertilizing = history.event_types[
            "fertilizing"
        ]

        assert fertilizing.count == 1

        assert fertilizing.last_at == datetime(
            2026,
            8,
            20,
            6,
            0,
        )

        assert (
            fertilizing.average_interval_days
            is None
        )

        assert (
            fertilizing.min_interval_days
            is None
        )

        assert (
            fertilizing.max_interval_days
            is None
        )

    finally:
        session.close()


@patch(
    "app.services.care_history_service.datetime"
)
def test_care_history_excludes_old_and_future_events(
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
        plant = create_plant(session)

        create_event(
            session=session,
            plant_id=plant.id,
            event_type="watering",
            occurred_at=datetime(
                2026,
                7,
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

        history = get_care_history(
            session=session,
            plant_id=plant.id,
            period_days=30,
        )

        assert history.total_events == 1

        assert (
            history.event_types[
                "watering"
            ].count
            == 1
        )

    finally:
        session.close()


@patch(
    "app.services.care_history_service.datetime"
)
def test_care_history_with_no_events(
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
        plant = create_plant(session)

        history = get_care_history(
            session=session,
            plant_id=plant.id,
        )

        assert history.total_events == 0
        assert history.event_types == {}

    finally:
        session.close()


def test_care_history_missing_plant():
    session = TestingSessionLocal()

    try:
        with pytest.raises(
            ValueError,
            match="Plant with id 999 not found",
        ):
            get_care_history(
                session=session,
                plant_id=999,
            )

    finally:
        session.close()


def test_care_history_rejects_invalid_period():
    session = TestingSessionLocal()

    try:
        plant = create_plant(session)

        with pytest.raises(
            ValueError,
            match=(
                "period_days must be greater than 0"
            ),
        ):
            get_care_history(
                session=session,
                plant_id=plant.id,
                period_days=0,
            )

    finally:
        session.close()