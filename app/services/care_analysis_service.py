from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import Plant, PlantEvent


@dataclass
class WateringAnalysis:
    plant_id: int
    total_events: int
    last_watered_at: datetime | None
    average_interval_days: float | None


def analyze_watering(
    session: Session,
    plant_id: int,
) -> WateringAnalysis:
    plant = session.get(
        Plant,
        plant_id,
    )

    if plant is None:
        raise ValueError(
            f"Plant with id {plant_id} not found"
        )

    watering_events = (
        session.query(PlantEvent)
        .filter(
            PlantEvent.plant_id == plant_id,
            PlantEvent.event_type == "watering",
        )
        .order_by(PlantEvent.occurred_at.asc())
        .all()
    )

    total_events = len(
        watering_events,
    )

    if total_events == 0:
        return WateringAnalysis(
            plant_id=plant_id,
            total_events=0,
            last_watered_at=None,
            average_interval_days=None,
        )

    last_watered_at = watering_events[-1].occurred_at

    if total_events == 1:
        return WateringAnalysis(
            plant_id=plant_id,
            total_events=1,
            last_watered_at=last_watered_at,
            average_interval_days=None,
        )

    intervals = []

    for previous_event, current_event in zip(
        watering_events,
        watering_events[1:],
    ):
        interval = (
            current_event.occurred_at
            - previous_event.occurred_at
        )

        intervals.append(
            interval.total_seconds()
            / 86400
        )

    average_interval_days = (
        sum(intervals)
        / len(intervals)
    )

    return WateringAnalysis(
        plant_id=plant_id,
        total_events=total_events,
        last_watered_at=last_watered_at,
        average_interval_days=average_interval_days,
    )