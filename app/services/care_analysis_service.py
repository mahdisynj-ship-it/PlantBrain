from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.database.models import Place, Plant, PlantEvent


@dataclass
class WateringAnalysis:
    plant_id: int
    total_events: int
    last_watered_at: datetime | None
    average_interval_days: float | None
    days_since_last_watering: float | None
    expected_next_watering_at: datetime | None
    watering_status: str


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

    place_timezone = _get_plant_timezone(
        session=session,
        plant=plant,
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
            days_since_last_watering=None,
            expected_next_watering_at=None,
            watering_status="unknown",
        )

    last_watered_at = watering_events[-1].occurred_at

    now = datetime.now(
        timezone.utc,
    )

    last_watered_at_utc = _ensure_utc(
        value=last_watered_at,
        local_timezone=place_timezone,
    )

    days_since_last_watering = (
        now - last_watered_at_utc
    ).total_seconds() / 86400

    days_since_last_watering = max(
        0.0,
        days_since_last_watering,
    )

    if total_events == 1:
        return WateringAnalysis(
            plant_id=plant_id,
            total_events=1,
            last_watered_at=last_watered_at,
            average_interval_days=None,
            days_since_last_watering=days_since_last_watering,
            expected_next_watering_at=None,
            watering_status="unknown",
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

    expected_next_watering_at = (
        last_watered_at
        + timedelta(
            days=average_interval_days,
        )
    )

    expected_next_watering_at_utc = _ensure_utc(
        value=expected_next_watering_at,
        local_timezone=place_timezone,
    )

    watering_status = _calculate_watering_status(
        now=now,
        expected_next_watering_at=expected_next_watering_at_utc,
        average_interval_days=average_interval_days,
    )

    return WateringAnalysis(
        plant_id=plant_id,
        total_events=total_events,
        last_watered_at=last_watered_at,
        average_interval_days=average_interval_days,
        days_since_last_watering=days_since_last_watering,
        expected_next_watering_at=expected_next_watering_at,
        watering_status=watering_status,
    )


def _get_plant_timezone(
    session: Session,
    plant: Plant,
) -> ZoneInfo:
    if plant.place_id is None:
        return ZoneInfo("UTC")

    place = session.get(
        Place,
        plant.place_id,
    )

    if place is None:
        return ZoneInfo("UTC")

    try:
        return ZoneInfo(
            place.timezone,
        )
    except Exception:
        return ZoneInfo("UTC")


def _ensure_utc(
    value: datetime,
    local_timezone: ZoneInfo,
) -> datetime:
    if value.tzinfo is None:
        value = value.replace(
            tzinfo=local_timezone,
        )

    return value.astimezone(
        timezone.utc,
    )


def _calculate_watering_status(
    now: datetime,
    expected_next_watering_at: datetime,
    average_interval_days: float,
) -> str:
    due_window = timedelta(
        days=max(
            1.0,
            average_interval_days * 0.15,
        ),
    )

    if now < expected_next_watering_at - due_window:
        return "not_due"

    if now <= expected_next_watering_at + due_window:
        return "due"

    return "overdue"