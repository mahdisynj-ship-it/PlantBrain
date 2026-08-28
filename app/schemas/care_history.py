from datetime import datetime

from pydantic import BaseModel


class EventTypeHistoryResponse(BaseModel):
    count: int
    last_at: datetime
    average_interval_days: float | None = None
    min_interval_days: float | None = None
    max_interval_days: float | None = None


class CareHistoryResponse(BaseModel):
    plant_id: int
    period_days: int
    total_events: int
    event_types: dict[
        str,
        EventTypeHistoryResponse,
    ]