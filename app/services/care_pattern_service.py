from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import sqrt

from sqlalchemy.orm import Session

from app.database.models import Plant, PlantEvent


@dataclass
class EventTypePattern:
    event_count: int
    interval_count: int
    average_interval_days: float | None
    interval_std_dev_days: float | None
    regularity: str
    trend: str


@dataclass
class CarePattern:
    plant_id: int
    period_days: int
    total_events: int
    event_types: dict[str, EventTypePattern]


def get_care_pattern(
    session: Session,
    plant_id: int,
    period_days: int = 90,
) -> CarePattern:
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

    period_end = now.replace(
        tzinfo=None,
    )

    events = (
        session.query(PlantEvent)
        .filter(
            PlantEvent.plant_id == plant_id,
            PlantEvent.occurred_at >= period_start,
            PlantEvent.occurred_at <= period_end,
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
        EventTypePattern,
    ] = {}

    for event_type, type_events in grouped_events.items():
        event_types[event_type] = (
            _analyze_event_type(
                type_events,
            )
        )

    return CarePattern(
        plant_id=plant_id,
        period_days=period_days,
        total_events=len(events),
        event_types=event_types,
    )


def _analyze_event_type(
    events: list[PlantEvent],
) -> EventTypePattern:
    event_count = len(events)

    if event_count < 2:
        return EventTypePattern(
            event_count=event_count,
            interval_count=0,
            average_interval_days=None,
            interval_std_dev_days=None,
            regularity="insufficient_data",
            trend="insufficient_data",
        )

    intervals = _calculate_intervals(
        events,
    )

    average_interval_days = (
        sum(intervals) / len(intervals)
    )

    interval_std_dev_days = (
        _calculate_population_std_dev(
            intervals,
            average_interval_days,
        )
    )

    regularity = _classify_regularity(
        average_interval_days=(
            average_interval_days
        ),
        std_dev_days=(
            interval_std_dev_days
        ),
        interval_count=len(intervals),
    )

    trend = _classify_trend(
        intervals,
    )

    return EventTypePattern(
        event_count=event_count,
        interval_count=len(intervals),
        average_interval_days=(
            average_interval_days
        ),
        interval_std_dev_days=(
            interval_std_dev_days
        ),
        regularity=regularity,
        trend=trend,
    )


def _calculate_intervals(
    events: list[PlantEvent],
) -> list[float]:
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

    return intervals


def _calculate_population_std_dev(
    values: list[float],
    mean: float,
) -> float:
    variance = sum(
        (value - mean) ** 2
        for value in values
    ) / len(values)

    return sqrt(
        variance,
    )


def _classify_regularity(
    average_interval_days: float,
    std_dev_days: float,
    interval_count: int,
) -> str:
    if interval_count < 2:
        return "insufficient_data"

    if average_interval_days <= 0:
        return "irregular"

    coefficient_of_variation = (
        std_dev_days
        / average_interval_days
    )

    if coefficient_of_variation <= 0.15:
        return "regular"

    if coefficient_of_variation <= 0.35:
        return "moderately_irregular"

    return "irregular"


def _classify_trend(
    intervals: list[float],
) -> str:
    if len(intervals) < 3:
        return "insufficient_data"

    first_half_average = (
        _average_first_half(
            intervals,
        )
    )

    second_half_average = (
        _average_second_half(
            intervals,
        )
    )

    if first_half_average <= 0:
        return "stable"

    relative_change = (
        second_half_average
        - first_half_average
    ) / first_half_average

    if relative_change >= 0.15:
        return "increasing_interval"

    if relative_change <= -0.15:
        return "decreasing_interval"

    return "stable"


def _average_first_half(
    values: list[float],
) -> float:
    midpoint = len(values) // 2

    first_half = values[
        :midpoint
    ]

    return sum(
        first_half,
    ) / len(
        first_half,
    )


def _average_second_half(
    values: list[float],
) -> float:
    midpoint = len(values) // 2

    second_half = values[
        midpoint:
    ]

    return sum(
        second_half,
    ) / len(
        second_half,
    )