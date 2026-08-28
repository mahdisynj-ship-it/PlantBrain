from datetime import datetime

from pydantic import BaseModel


class WateringAnalysisResponse(BaseModel):
    plant_id: int
    total_events: int
    last_watered_at: datetime | None
    average_interval_days: float | None