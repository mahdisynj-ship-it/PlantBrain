from datetime import datetime, timedelta, timezone

from app.utils.datetime_utils import (
    local_datetime_to_utc_naive,
    utc_datetime_to_local,
    utc_naive_to_aware,
)


def test_tehran_local_datetime_to_utc_naive():
    local_time = datetime(
        2026,
        8,
        28,
        10,
        0,
    )

    result = local_datetime_to_utc_naive(
        value=local_time,
        timezone_name="Asia/Tehran",
    )

    assert result == datetime(
        2026,
        8,
        28,
        6,
        30,
    )

    assert result.tzinfo is None


def test_bogota_local_datetime_to_utc_naive():
    local_time = datetime(
        2026,
        8,
        28,
        10,
        0,
    )

    result = local_datetime_to_utc_naive(
        value=local_time,
        timezone_name="America/Bogota",
    )

    assert result == datetime(
        2026,
        8,
        28,
        15,
        0,
    )

    assert result.tzinfo is None


def test_aware_datetime_respects_existing_timezone():
    aware_time = datetime(
        2026,
        8,
        28,
        10,
        0,
        tzinfo=timezone(
            timedelta(hours=2),
        ),
    )

    result = local_datetime_to_utc_naive(
        value=aware_time,
        timezone_name="Asia/Tehran",
    )

    assert result == datetime(
        2026,
        8,
        28,
        8,
        0,
    )

    assert result.tzinfo is None


def test_utc_naive_to_aware():
    stored_time = datetime(
        2026,
        8,
        28,
        6,
        30,
    )

    result = utc_naive_to_aware(
        stored_time,
    )

    assert result == datetime(
        2026,
        8,
        28,
        6,
        30,
        tzinfo=timezone.utc,
    )


def test_utc_datetime_to_tehran_local():
    stored_time = datetime(
        2026,
        8,
        28,
        6,
        30,
    )

    result = utc_datetime_to_local(
        value=stored_time,
        timezone_name="Asia/Tehran",
    )

    assert result.hour == 10
    assert result.minute == 0

    assert (
        result.utcoffset()
        == timedelta(
            hours=3,
            minutes=30,
        )
    )


def test_utc_datetime_to_bogota_local():
    stored_time = datetime(
        2026,
        8,
        28,
        15,
        0,
    )

    result = utc_datetime_to_local(
        value=stored_time,
        timezone_name="America/Bogota",
    )

    assert result.hour == 10
    assert result.minute == 0

    assert (
        result.utcoffset()
        == timedelta(hours=-5)
    )