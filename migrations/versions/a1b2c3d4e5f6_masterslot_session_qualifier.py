"""Add session and qualifier to masterslot

Revision ID: a1b2c3d4e5f6
Revises: 9666c6f66d21
Create Date: 2026-05-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "9666c6f66d21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("masterslot") as batch_op:
        batch_op.add_column(
            sa.Column(
                "session",
                sqlmodel.sql.sqltypes.AutoString(),
                nullable=False,
                server_default="AM",
            )
        )
        batch_op.add_column(
            sa.Column("qualifier", sqlmodel.sql.sqltypes.AutoString(), nullable=True)
        )

    # Backfill session from existing time_block values where possible.
    op.execute(
        "UPDATE masterslot SET session = CASE WHEN time_block IN ('AM', 'PM') "
        "THEN time_block ELSE 'AM' END"
    )


def downgrade() -> None:
    with op.batch_alter_table("masterslot") as batch_op:
        batch_op.drop_column("qualifier")
        batch_op.drop_column("session")
