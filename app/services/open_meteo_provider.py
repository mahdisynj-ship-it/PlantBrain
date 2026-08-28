from datetime import datetime, timedelta, timezone

import httpx

from app.services.weather_provider import WeatherData
from app.utils.datetime_utils import (
    local_datetime_to_utc_naive,
)


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


def get_current_weather(
    latitude: float,
    longitude: float,
    timezone_name: str,
) -> WeatherData:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "weather_code"
        ),
        "timezone": timezone_name,
    }

    response = httpx.get(
        OPEN_METEO_URL,
        params=params,
        timeout=10.0,
    )

    response.raise_for_status()

    data = response.json()
    current = data["current"]

    recorded_at_local = datetime.fromisoformat(
        current["time"],
    )

    recorded_at_utc = local_datetime_to_utc_naive(
        value=recorded_at_local,
        timezone_name=timezone_name,
    )

    return WeatherData(
        temperature=current.get("temperature_2m"),
        humidity=current.get(
            "relative_humidity_2m"
        ),
        weather_condition=(
            _weather_code_to_condition(
                current.get("weather_code"),
            )
        ),
        recorded_at=recorded_at_utc,
        source="open-meteo",
    )


def get_historical_weather(
    latitude: float,
    longitude: float,
    occurred_at: datetime,
    timezone_name: str,
) -> WeatherData:
    occurred_at_local = _to_local_naive(
        value=occurred_at,
        timezone_name=timezone_name,
    )

    date_string = (
        occurred_at_local.date().isoformat()
    )

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
        "timezone": timezone_name,
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
        occurred_at=occurred_at_local,
    )

    recorded_at_local = datetime.fromisoformat(
        hourly["time"][target_index],
    )

    recorded_at_utc = local_datetime_to_utc_naive(
        value=recorded_at_local,
        timezone_name=timezone_name,
    )

    return WeatherData(
        temperature=(
            hourly["temperature_2m"][
                target_index
            ]
        ),
        humidity=(
            hourly[
                "relative_humidity_2m"
            ][target_index]
        ),
        weather_condition=(
            _weather_code_to_condition(
                hourly["weather_code"][
                    target_index
                ],
            )
        ),
        recorded_at=recorded_at_utc,
        source="open-meteo-historical",
    )


def get_weather_for_time(
    latitude: float,
    longitude: float,
    occurred_at: datetime,
    timezone_name: str,
) -> WeatherData:
    now = datetime.now(
        timezone.utc,
    )

    occurred_at_utc = _to_utc(
        value=occurred_at,
        timezone_name=timezone_name,
    )

    if abs(
        now - occurred_at_utc
    ) <= timedelta(hours=3):
        return get_current_weather(
            latitude=latitude,
            longitude=longitude,
            timezone_name=timezone_name,
        )

    return get_historical_weather(
        latitude=latitude,
        longitude=longitude,
        occurred_at=occurred_at,
        timezone_name=timezone_name,
    )


def _to_utc(
    value: datetime,
    timezone_name: str,
) -> datetime:
    utc_naive = local_datetime_to_utc_naive(
        value=value,
        timezone_name=timezone_name,
    )

    return utc_naive.replace(
        tzinfo=timezone.utc,
    )


def _to_local_naive(
    value: datetime,
    timezone_name: str,
) -> datetime:
    if value.tzinfo is None:
        return value

    return value.astimezone(
        _get_timezone(
            timezone_name,
        )
    ).replace(
        tzinfo=None,
    )


def _get_timezone(
    timezone_name: str,
):
    from zoneinfo import ZoneInfo

    return ZoneInfo(
        timezone_name,
    )


def _find_closest_hour_index(
    times: list[str],
    occurred_at: datetime,
) -> int:
    if not times:
        raise ValueError(
            "Historical weather response "
            "contains no hourly data"
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
        96: (
            "thunderstorm_with_light_hail"
        ),
        99: (
            "thunderstorm_with_heavy_hail"
        ),
    }

    return conditions.get(
        weather_code,
        "unknown",
    )