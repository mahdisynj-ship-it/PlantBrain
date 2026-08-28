"""normalize event and weather times to utc

Revision ID: ed09dfbadb50
Revises: d344c83dd447
Create Date: 2026-08-28

"""

from datetime import datetime, timezone
from typing import Sequence, Union
from zoneinfo import ZoneInfo

from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = "ed09dfbadb50"
down_revision: Union[str, Sequence[str], None] = (
    "d344c83dd447"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Convert existing local-naive semantic timestamps
    to UTC-naive storage.

    Only timestamps whose plant has a Place are
    converted, because the Place timezone tells us
    how to interpret the old naive value.

    Rows without a Place are left unchanged and are
    treated as UTC under the new application contract.
    """
    connection = op.get_bind()

    _convert_event_times_to_utc(
        connection,
    )

    _convert_weather_times_to_utc(
        connection,
    )


def downgrade() -> None:
    """
    Convert UTC-naive timestamps back to local-naive
    values using each plant's current Place timezone.
    """
    connection = op.get_bind()

    _convert_event_times_to_local(
        connection,
    )

    _convert_weather_times_to_local(
        connection,
    )


def _convert_event_times_to_utc(
    connection,
) -> None:
    rows = connection.execute(
        text(
            """
            SELECT
                plant_events.id AS event_id,
                plant_events.occurred_at AS occurred_at,
                places.timezone AS timezone_name
            FROM plant_events
            JOIN plants
                ON plants.id = plant_events.plant_id
            JOIN places
                ON places.id = plants.place_id
            WHERE plant_events.occurred_at IS NOT NULL
            """
        )
    ).mappings().all()

    for row in rows:
        local_value = _parse_datetime(
            row["occurred_at"],
        )

        utc_value = _local_to_utc_naive(
            value=local_value,
            timezone_name=row["timezone_name"],
        )

        connection.execute(
            text(
                """
                UPDATE plant_events
                SET occurred_at = :occurred_at
                WHERE id = :event_id
                """
            ),
            {
                "occurred_at": _format_datetime(
                    utc_value,
                ),
                "event_id": row["event_id"],
            },
        )


def _convert_weather_times_to_utc(
    connection,
) -> None:
    rows = connection.execute(
        text(
            """
            SELECT
                weather_snapshots.id AS snapshot_id,
                weather_snapshots.recorded_at AS recorded_at,
                places.timezone AS timezone_name
            FROM weather_snapshots
            JOIN plant_events
                ON plant_events.id =
                   weather_snapshots.event_id
            JOIN plants
                ON plants.id =
                   plant_events.plant_id
            JOIN places
                ON places.id = plants.place_id
            WHERE weather_snapshots.recorded_at
                  IS NOT NULL
            """
        )
    ).mappings().all()

    for row in rows:
        local_value = _parse_datetime(
            row["recorded_at"],
        )

        utc_value = _local_to_utc_naive(
            value=local_value,
            timezone_name=row["timezone_name"],
        )

        connection.execute(
            text(
                """
                UPDATE weather_snapshots
                SET recorded_at = :recorded_at
                WHERE id = :snapshot_id
                """
            ),
            {
                "recorded_at": _format_datetime(
                    utc_value,
                ),
                "snapshot_id": row["snapshot_id"],
            },
        )


def _convert_event_times_to_local(
    connection,
) -> None:
    rows = connection.execute(
        text(
            """
            SELECT
                plant_events.id AS event_id,
                plant_events.occurred_at AS occurred_at,
                places.timezone AS timezone_name
            FROM plant_events
            JOIN plants
                ON plants.id = plant_events.plant_id
            JOIN places
                ON places.id = plants.place_id
            WHERE plant_events.occurred_at IS NOT NULL
            """
        )
    ).mappings().all()

    for row in rows:
        utc_value = _parse_datetime(
            row["occurred_at"],
        )

        local_value = _utc_to_local_naive(
            value=utc_value,
            timezone_name=row["timezone_name"],
        )

        connection.execute(
            text(
                """
                UPDATE plant_events
                SET occurred_at = :occurred_at
                WHERE id = :event_id
                """
            ),
            {
                "occurred_at": _format_datetime(
                    local_value,
                ),
                "event_id": row["event_id"],
            },
        )


def _convert_weather_times_to_local(
    connection,
) -> None:
    rows = connection.execute(
        text(
            """
            SELECT
                weather_snapshots.id AS snapshot_id,
                weather_snapshots.recorded_at AS recorded_at,
                places.timezone AS timezone_name
            FROM weather_snapshots
            JOIN plant_events
                ON plant_events.id =
                   weather_snapshots.event_id
            JOIN plants
                ON plants.id =
                   plant_events.plant_id
            JOIN places
                ON places.id = plants.place_id
            WHERE weather_snapshots.recorded_at
                  IS NOT NULL
            """
        )
    ).mappings().all()

    for row in rows:
        utc_value = _parse_datetime(
            row["recorded_at"],
        )

        local_value = _utc_to_local_naive(
            value=utc_value,
            timezone_name=row["timezone_name"],
        )

        connection.execute(
            text(
                """
                UPDATE weather_snapshots
                SET recorded_at = :recorded_at
                WHERE id = :snapshot_id
                """
            ),
            {
                "recorded_at": _format_datetime(
                    local_value,
                ),
                "snapshot_id": row["snapshot_id"],
            },
        )


def _local_to_utc_naive(
    value: datetime,
    timezone_name: str,
) -> datetime:
    if value.tzinfo is None:
        local_timezone = ZoneInfo(
            timezone_name,
        )

        value = value.replace(
            tzinfo=local_timezone,
        )

    return value.astimezone(
        timezone.utc,
    ).replace(
        tzinfo=None,
    )


def _utc_to_local_naive(
    value: datetime,
    timezone_name: str,
) -> datetime:
    if value.tzinfo is None:
        value = value.replace(
            tzinfo=timezone.utc,
        )
    else:
        value = value.astimezone(
            timezone.utc,
        )

    local_timezone = ZoneInfo(
        timezone_name,
    )

    return value.astimezone(
        local_timezone,
    ).replace(
        tzinfo=None,
    )


def _parse_datetime(
    value,
) -> datetime:
    if isinstance(
        value,
        datetime,
    ):
        return value

    return datetime.fromisoformat(
        str(value),
    )


def _format_datetime(
    value: datetime,
) -> str:
    return value.isoformat(
        sep=" ",
        timespec="microseconds",
    )