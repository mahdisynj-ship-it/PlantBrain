from datetime import datetime

from pydantic import BaseModel


class WateringInsightResponse(BaseModel):
    status: str

    days_since_last_watering: float | None = None

    average_interval_days: float | None = None

    expected_next_watering_at: datetime | None = None


class PatternInsightResponse(BaseModel):
    regularity: str
    trend: str


class RecommendationResponse(BaseModel):
    action: str
    priority: str
    message: str


class PlantInsightResponse(BaseModel):
    plant_id: int
    plant_name: str

    watering: WateringInsightResponse

    pattern: PatternInsightResponse

    recommendation: RecommendationResponse