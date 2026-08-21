"""Add cascade delete to plant events

Revision ID: 2c08861a1016
Revises: a54680d65dea
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2c08861a1016"
down_revision: Union[str, Sequence[str], None] = "a54680d65dea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ON DELETE CASCADE to plant_events.plant_id."""

    with op.batch_alter_table(
        "plant_events",
        recreate="always",
    ) as batch_op:
        batch_op.create_foreign_key(
            "fk_plant_events_plant_id",
            "plants",
            ["plant_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    """Remove ON DELETE CASCADE from plant_events.plant_id."""

    with op.batch_alter_table(
        "plant_events",
        recreate="always",
    ) as batch_op:
        batch_op.drop_constraint(
            "fk_plant_events_plant_id",
            type_="foreignkey",
        )

        batch_op.create_foreign_key(
            None,
            "plants",
            ["plant_id"],
            ["id"],
        )