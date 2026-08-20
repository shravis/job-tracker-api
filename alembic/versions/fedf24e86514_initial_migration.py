"""Initial migration

Revision ID: fedf24e86514
Revises:
Create Date: 2026-08-18 23:02:06.866302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "fedf24e86514"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()

    if "users" not in tables:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("username", sa.Text(), nullable=False),
            sa.Column("password", sa.Text(), nullable=False),
            sa.Column(
                "token_version",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
            sa.UniqueConstraint("username", name="users_username_key"),
        )

    if "jobs" not in tables:
        op.create_table(
            "jobs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("company", sa.Text(), nullable=False),
            sa.Column("position", sa.Text(), nullable=False),
            sa.Column("status", sa.Text(), nullable=False),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id"),
                nullable=False,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
        )

    inspector = inspect(bind)
    if "jobs" in inspector.get_table_names():
        indexes = {idx["name"] for idx in inspector.get_indexes("jobs")}
        if "idx_jobs_company" not in indexes:
            op.create_index("idx_jobs_company", "jobs", ["company"])
        if "idx_jobs_status" not in indexes:
            op.create_index("idx_jobs_status", "jobs", ["status"])
        if "idx_jobs_user_id" not in indexes:
            columns = {col["name"] for col in inspector.get_columns("jobs")}
            if "user_id" in columns:
                op.create_index("idx_jobs_user_id", "jobs", ["user_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()

    if "jobs" in tables:
        indexes = {idx["name"] for idx in inspector.get_indexes("jobs")}
        if "idx_jobs_user_id" in indexes:
            op.drop_index("idx_jobs_user_id", table_name="jobs")
        if "idx_jobs_status" in indexes:
            op.drop_index("idx_jobs_status", table_name="jobs")
        if "idx_jobs_company" in indexes:
            op.drop_index("idx_jobs_company", table_name="jobs")
        op.drop_table("jobs")

    if "users" in inspector.get_table_names():
        op.drop_table("users")
