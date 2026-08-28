from datetime import datetime, timedelta, timezone

import httpx

from app.services.weather_provider import WeatherData


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


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


def get_historical_weather(
    latitude: float,
    longitude: float,
    occurred_at: datetime,
) -> WeatherData:
    date_string = occurred_at.date().isoformat()

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": date_string,
        "end_date": date_string,
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "weather_code"
        ),
        "timezone": "auto",
    }

    response = httpx.get(
        OPEN_METEO_ARCHIVE_URL,
        params=params,
        timeout=10.0,
    )

    response.raise_for_status()

    data = response.json()
    hourly = data["hourly"]

    target_index = _find_closest_hour_index(
        times=hourly["time"],
        occurred_at=occurred_at,
    )

    recorded_at = datetime.fromisoformat(
        hourly["time"][target_index],
    )

    return WeatherData(
        temperature=hourly["temperature_2m"][target_index],
        humidity=hourly["relative_humidity_2m"][target_index],
        weather_condition=_weather_code_to_condition(
            hourly["weather_code"][target_index],
        ),
        recorded_at=recorded_at,
        source="open-meteo-historical",
    )


def get_weather_for_time(
    latitude: float,
    longitude: float,
    occurred_at: datetime,
) -> WeatherData:
    now = datetime.now(timezone.utc)

    occurred_at_utc = _ensure_utc(
        occurred_at,
    )

    if abs(now - occurred_at_utc) <= timedelta(hours=3):
        return get_current_weather(
            latitude=latitude,
            longitude=longitude,
        )

    return get_historical_weather(
        latitude=latitude,
        longitude=longitude,
        occurred_at=occurred_at,
    )


def _ensure_utc(
    value: datetime,
) -> datetime:
    if value.tzinfo is None:
        return value.replace(
            tzinfo=timezone.utc,
        )

    return value.astimezone(
        timezone.utc,
    )


def _find_closest_hour_index(
    times: list[str],
    occurred_at: datetime,
) -> int:
    if not times:
        raise ValueError(
            "Historical weather response contains no hourly data"
        )

    target = occurred_at.replace(
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=None,
    )

    parsed_times = [
        datetime.fromisoformat(value)
        for value in times
    ]

    return min(
        range(len(parsed_times)),
        key=lambda index: abs(
            parsed_times[index] - target
        ),
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