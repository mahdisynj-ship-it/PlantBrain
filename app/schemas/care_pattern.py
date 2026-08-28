from pydantic import BaseModel


class EventTypePatternResponse(BaseModel):
    event_count: int
    interval_count: int

    average_interval_days: float | None = None
    interval_std_dev_days: float | None = None

    regularity: str
    trend: str


class CarePatternResponse(BaseModel):
    plant_id: int
    period_days: int
    total_events: int

    event_types: dict[
        str,
        EventTypePatternResponse,
    ]