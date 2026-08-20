"""Add timestamps to jobs

Revision ID: 8b3eed90bc29
Revises: fedf24e86514
Create Date: 2026-08-18 23:07:46.682301

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "8b3eed90bc29"
down_revision: Union[str, Sequence[str], None] = "fedf24e86514"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "jobs" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("jobs")}

    if "created_at" not in columns:
        op.add_column(
            "jobs",
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
        )

    if "updated_at" not in columns:
        op.add_column(
            "jobs",
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "jobs" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("jobs")}
    if "updated_at" in columns:
        op.drop_column("jobs", "updated_at")
    if "created_at" in columns:
        op.drop_column("jobs", "created_at")
