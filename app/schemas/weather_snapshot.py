from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateWeatherSnapshot(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    temperature: float | None = None

    humidity: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    weather_condition: str | None = Field(
        default=None,
        max_length=100,
    )

    recorded_at: datetime

    source: str | None = Field(
        default=None,
        max_length=100,
    )


class UpdateWeatherSnapshot(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    temperature: float | None = None

    humidity: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    weather_condition: str | None = Field(
        default=None,
        max_length=100,
    )

    recorded_at: datetime | None = None

    source: str | None = Field(
        default=None,
        max_length=100,
    )


class WeatherSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    temperature: float | None = None
    humidity: float | None = None
    weather_condition: str | None = None
    recorded_at: datetime
    source: str | None = None