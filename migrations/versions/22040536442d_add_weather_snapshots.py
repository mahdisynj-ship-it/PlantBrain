"""Add weather snapshots

Revision ID: 22040536442d
Revises: 2c08861a1016
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "22040536442d"
down_revision: Union[str, Sequence[str], None] = "2c08861a1016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "weather_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("humidity", sa.Float(), nullable=True),
        sa.Column("weather_condition", sa.String(length=100), nullable=True),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["plant_events.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
    )

    op.create_index(
        "ix_weather_snapshots_event_id",
        "weather_snapshots",
        ["event_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_weather_snapshots_event_id",
        table_name="weather_snapshots",
    )

    op.drop_table("weather_snapshots")