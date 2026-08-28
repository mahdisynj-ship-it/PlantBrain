from datetime import datetime

from pydantic import BaseModel


class WateringAnalysisResponse(BaseModel):
    plant_id: int
    total_events: int
    last_watered_at: datetime | None
    average_interval_days: float | None
    days_since_last_watering: float | None
    expected_next_watering_at: datetime | None
    watering_status: str