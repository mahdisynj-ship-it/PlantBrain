from dataclasses import dataclass
from datetime import datetime


@dataclass
class WeatherData:
    temperature: float | None
    humidity: float | None
    weather_condition: str | None
    recorded_at: datetime
    source: str