from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from app.services.open_meteo_provider import (
    _weather_code_to_condition,
    get_current_weather,
    get_historical_weather,
    get_weather_for_time,
)


def test_weather_code_to_condition():
    assert _weather_code_to_condition(0) == "clear"
    assert _weather_code_to_condition(61) == "light_rain"
    assert _weather_code_to_condition(95) == "thunderstorm"


def test_weather_code_to_condition_unknown():
    assert _weather_code_to_condition(999) == "unknown"


def test_weather_code_to_condition_none():
    assert _weather_code_to_condition(None) is None


@patch("app.services.open_meteo_provider.httpx.get")
def test_get_current_weather(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = {
        "current": {
            "temperature_2m": 22.5,
            "relative_humidity_2m": 68,
            "weather_code": 2,
            "time": "2026-08-28T09:30",
        }
    }

    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    weather = get_current_weather(
        latitude=37.2073,
        longitude=50.0039,
    )

    assert weather.temperature == 22.5
    assert weather.humidity == 68
    assert weather.weather_condition == "partly_cloudy"
    assert weather.recorded_at == datetime(
        2026,
        8,
        28,
        9,
        30,
    )
    assert weather.source == "open-meteo"

    mock_get.assert_called_once()


@patch("app.services.open_meteo_provider.httpx.get")
def test_get_current_weather_sends_coordinates(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = {
        "current": {
            "temperature_2m": 18.0,
            "relative_humidity_2m": 75,
            "weather_code": 61,
            "time": "2026-08-28T08:00",
        }
    }

    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    get_current_weather(
        latitude=37.2073,
        longitude=50.0039,
    )

    _, kwargs = mock_get.call_args
    params = kwargs["params"]

    assert params["latitude"] == 37.2073
    assert params["longitude"] == 50.0039
    assert params["timezone"] == "auto"
    assert "temperature_2m" in params["current"]
    assert "relative_humidity_2m" in params["current"]
    assert "weather_code" in params["current"]


@patch("app.services.open_meteo_provider.httpx.get")
def test_get_historical_weather(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = {
        "hourly": {
            "time": [
                "2026-08-20T08:00",
                "2026-08-20T09:00",
                "2026-08-20T10:00",
            ],
            "temperature_2m": [
                20.0,
                21.5,
                23.0,
            ],
            "relative_humidity_2m": [
                80,
                72,
                65,
            ],
            "weather_code": [
                3,
                2,
                1,
            ],
        }
    }

    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    weather = get_historical_weather(
        latitude=37.2073,
        longitude=50.0039,
        occurred_at=datetime(
            2026,
            8,
            20,
            9,
            20,
        ),
    )

    assert weather.temperature == 21.5
    assert weather.humidity == 72
    assert weather.weather_condition == "partly_cloudy"
    assert weather.recorded_at == datetime(
        2026,
        8,
        20,
        9,
        0,
    )
    assert weather.source == "open-meteo-historical"


@patch("app.services.open_meteo_provider.get_current_weather")
def test_get_weather_for_time_uses_current_weather(
    mock_current_weather,
):
    mock_current_weather.return_value = Mock()

    occurred_at = datetime.now(
        timezone.utc,
    ) - timedelta(hours=1)

    result = get_weather_for_time(
        latitude=37.2073,
        longitude=50.0039,
        occurred_at=occurred_at,
    )

    mock_current_weather.assert_called_once_with(
        latitude=37.2073,
        longitude=50.0039,
    )

    assert result == mock_current_weather.return_value


@patch("app.services.open_meteo_provider.get_historical_weather")
def test_get_weather_for_time_uses_historical_weather(
    mock_historical_weather,
):
    mock_historical_weather.return_value = Mock()

    occurred_at = datetime.now(
        timezone.utc,
    ) - timedelta(days=2)

    result = get_weather_for_time(
        latitude=37.2073,
        longitude=50.0039,
        occurred_at=occurred_at,
    )

    mock_historical_weather.assert_called_once_with(
        latitude=37.2073,
        longitude=50.0039,
        occurred_at=occurred_at,
    )

    assert result == mock_historical_weather.return_value