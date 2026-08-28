from datetime import datetime

import httpx

from app.services.weather_provider import WeatherData


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_current_weather(
    latitude: float,
    longitude: float,
) -> WeatherData:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "weather_code"
        ),
        "timezone": "auto",
    }

    response = httpx.get(
        OPEN_METEO_URL,
        params=params,
        timeout=10.0,
    )

    response.raise_for_status()

    data = response.json()
    current = data["current"]

    return WeatherData(
        temperature=current.get("temperature_2m"),
        humidity=current.get("relative_humidity_2m"),
        weather_condition=_weather_code_to_condition(
            current.get("weather_code"),
        ),
        recorded_at=datetime.fromisoformat(
            current["time"],
        ),
        source="open-meteo",
    )


def _weather_code_to_condition(
    weather_code: int | None,
) -> str | None:
    if weather_code is None:
        return None

    conditions = {
        0: "clear",
        1: "mainly_clear",
        2: "partly_cloudy",
        3: "overcast",
        45: "fog",
        48: "rime_fog",
        51: "light_drizzle",
        53: "moderate_drizzle",
        55: "dense_drizzle",
        56: "light_freezing_drizzle",
        57: "dense_freezing_drizzle",
        61: "light_rain",
        63: "moderate_rain",
        65: "heavy_rain",
        66: "light_freezing_rain",
        67: "heavy_freezing_rain",
        71: "light_snow",
        73: "moderate_snow",
        75: "heavy_snow",
        77: "snow_grains",
        80: "light_rain_showers",
        81: "moderate_rain_showers",
        82: "violent_rain_showers",
        85: "light_snow_showers",
        86: "heavy_snow_showers",
        95: "thunderstorm",
        96: "thunderstorm_with_light_hail",
        99: "thunderstorm_with_heavy_hail",
    }

    return conditions.get(
        weather_code,
        "unknown",
    )