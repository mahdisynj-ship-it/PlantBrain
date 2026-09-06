from datetime import datetime

import pytest

from app.schemas.plant import CreatePlant
from app.schemas.plant_event import CreatePlantEvent
from app.services.event_service import create_event
from app.services.plant_insight_service import get_plant_insight
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


def test_get_plant_insight_with_regular_watering(
    db_session,
):
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

    result = get_plant_insight(
        session=db_session,
        plant_id=plant.id,
    )

    assert result.plant_id == plant.id
    assert result.plant_name == "فیکوس تست"

    assert result.watering.status in [
        "not_due",
        "due",
        "overdue",
    ]

    assert result.pattern.regularity == "regular"

    assert (
        result.pattern.trend
        == "insufficient_data"
    )

    assert result.recommendation.action in [
        "monitor",
        "water_soon",
        "water_now",
        "collect_more_data",
    ]


def test_get_plant_insight_missing_plant(
    db_session,
):
    with pytest.raises(
        ValueError,
        match="Plant with id 999 not found",
    ):
        get_plant_insight(
            session=db_session,
            plant_id=999,
        )