from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def local_datetime_to_utc_naive(
    value: datetime,
    timezone_name: str,
) -> datetime:
    """
    Convert a datetime to naive UTC for database storage.

    If value is naive, it is interpreted as local time in timezone_name.
    If value is already timezone-aware, its existing timezone is respected.
    """
    if value.tzinfo is None:
        local_timezone = ZoneInfo(
            timezone_name,
        )

        value = value.replace(
            tzinfo=local_timezone,
        )

    utc_value = value.astimezone(
        timezone.utc,
    )

    return utc_value.replace(
        tzinfo=None,
    )


def utc_naive_to_aware(
    value: datetime,
) -> datetime:
    """
    Interpret a naive database datetime as UTC.

    If the value is already timezone-aware,
    convert it to UTC.
    """
    if value.tzinfo is None:
        return value.replace(
            tzinfo=timezone.utc,
        )

    return value.astimezone(
        timezone.utc,
    )


def utc_datetime_to_local(
    value: datetime,
    timezone_name: str,
) -> datetime:
    """
    Convert a stored UTC datetime to a timezone-aware local datetime.
    """
    utc_value = utc_naive_to_aware(
        value,
    )

    local_timezone = ZoneInfo(
        timezone_name,
    )

    return utc_value.astimezone(
        local_timezone,
    )