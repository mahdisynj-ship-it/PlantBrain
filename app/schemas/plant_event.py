from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreatePlantEvent(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    plant_id: int = Field(gt=0)

    event_type: str = Field(
        min_length=1,
        max_length=50,
    )

    occurred_at: datetime

    notes: str | None = None

    amount: float | None = Field(
        default=None,
        ge=0,
    )

    unit: str | None = Field(
        default=None,
        max_length=30,
    )

    event_metadata: dict | None = None