"""Add places and plant place relation

Revision ID: e2edb431e856
Revises: 22040536442d
Create Date: 2026-08-25 14:37:39.465717
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e2edb431e856"
down_revision: Union[str, Sequence[str], None] = "22040536442d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "places",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column(
        "plants",
        sa.Column(
            "place_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_plants_place_id",
        "plants",
        ["place_id"],
        unique=False,
    )

    with op.batch_alter_table("plants") as batch_op:
        batch_op.create_foreign_key(
            "fk_plants_place_id_places",
            "places",
            ["place_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("plants") as batch_op:
        batch_op.drop_constraint(
            "fk_plants_place_id_places",
            type_="foreignkey",
        )

    op.drop_index(
        "ix_plants_place_id",
        table_name="plants",
    )

    op.drop_column(
        "plants",
        "place_id",
    )

    op.drop_table("places")