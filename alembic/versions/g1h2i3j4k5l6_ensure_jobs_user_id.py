"""Ensure jobs.user_id exists (idempotent repair).

Revision ID: g1h2i3j4k5l6
Revises: f9a0b1c2d3e4
Create Date: 2026-08-20 21:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision: str = "g1h2i3j4k5l6"
down_revision: Union[str, Sequence[str], None] = "f9a0b1c2d3e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "jobs" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("jobs")}
    if "user_id" not in columns:
        op.add_column(
            "jobs",
            sa.Column("user_id", sa.Integer(), nullable=True),
        )
        bind.execute(text(
            """
            UPDATE jobs
            SET user_id = (SELECT id FROM users ORDER BY id LIMIT 1)
            WHERE user_id IS NULL
              AND EXISTS (SELECT 1 FROM users)
            """
        ))
        orphan_count = bind.execute(
            text("SELECT COUNT(*) FROM jobs WHERE user_id IS NULL")
        ).scalar()
        if orphan_count:
            raise RuntimeError(
                f"Refusing to continue: {orphan_count} job(s) have no user_id "
                "and no user exists to assign them to. This transaction will "
                "roll back. Create at least one user, then re-run "
                "`alembic upgrade head`. Jobs were not deleted."
            )
        op.alter_column("jobs", "user_id", nullable=False)

    inspector = inspect(bind)
    fks = {fk["name"] for fk in inspector.get_foreign_keys("jobs")}
    if "fk_jobs_user_id_users" not in fks:
        columns = {col["name"] for col in inspector.get_columns("jobs")}
        if "user_id" in columns:
            op.create_foreign_key(
                "fk_jobs_user_id_users",
                "jobs",
                "users",
                ["user_id"],
                ["id"],
            )

    indexes = {idx["name"] for idx in inspector.get_indexes("jobs")}
    if "idx_jobs_user_id" not in indexes:
        columns = {col["name"] for col in inspector.get_columns("jobs")}
        if "user_id" in columns:
            op.create_index("idx_jobs_user_id", "jobs", ["user_id"])


def downgrade() -> None:
    pass
