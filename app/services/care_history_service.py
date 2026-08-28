from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.database.models import Plant, PlantEvent


@dataclass
class EventTypeHistory:
    count: int
    last_at: datetime
    average_interval_days: float | None
    min_interval_days: float | None
    max_interval_days: float | None


@dataclass
class CareHistory:
    plant_id: int
    period_days: int
    total_events: int
    event_types: dict[str, EventTypeHistory]


def get_care_history(
    session: Session,
    plant_id: int,
    period_days: int = 30,
) -> CareHistory:
    plant = session.get(
        Plant,
        plant_id,
    )

    if plant is None:
        raise ValueError(
            f"Plant with id {plant_id} not found"
        )

    if period_days <= 0:
        raise ValueError(
            "period_days must be greater than 0"
        )

    now = datetime.now(
        timezone.utc,
    )

    period_start = (
        now - timedelta(days=period_days)
    ).replace(
        tzinfo=None,
    )

    events = (
        session.query(PlantEvent)
        .filter(
            PlantEvent.plant_id == plant_id,
            PlantEvent.occurred_at >= period_start,
            PlantEvent.occurred_at
            <= now.replace(tzinfo=None),
        )
        .order_by(
            PlantEvent.occurred_at.asc(),
        )
        .all()
    )

    grouped_events: dict[
        str,
        list[PlantEvent],
    ] = {}

    for event in events:
        grouped_events.setdefault(
            event.event_type,
            [],
        ).append(event)

    event_types: dict[
        str,
        EventTypeHistory,
    ] = {}

    for event_type, type_events in grouped_events.items():
        event_types[event_type] = (
            _analyze_event_type(
                type_events,
            )
        )

    return CareHistory(
        plant_id=plant_id,
        period_days=period_days,
        total_events=len(events),
        event_types=event_types,
    )


def _analyze_event_type(
    events: list[PlantEvent],
) -> EventTypeHistory:
    last_at = events[-1].occurred_at

    if len(events) == 1:
        return EventTypeHistory(
            count=1,
            last_at=last_at,
            average_interval_days=None,
            min_interval_days=None,
            max_interval_days=None,
        )

    intervals: list[float] = []

    for previous_event, current_event in zip(
        events,
        events[1:],
    ):
        interval = (
            current_event.occurred_at
            - previous_event.occurred_at
        )

        intervals.append(
            interval.total_seconds() / 86400
        )

    return EventTypeHistory(
        count=len(events),
        last_at=last_at,
        average_interval_days=(
            sum(intervals) / len(intervals)
        ),
        min_interval_days=min(intervals),
        max_interval_days=max(intervals),
    )