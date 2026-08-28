"""add timezone to places

Revision ID: d344c83dd447
Revises: e2edb431e856
Create Date: 2026-08-28
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d344c83dd447"
down_revision: Union[str, Sequence[str], None] = "e2edb431e856"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "places",
        sa.Column(
            "timezone",
            sa.String(length=100),
            nullable=False,
            server_default="Asia/Tehran",
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "places",
        "timezone",
    )