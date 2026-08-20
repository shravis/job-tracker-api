"""Repair job ownership, status values, and token_version

Revision ID: c4f1a2b3d4e5
Revises: 8b3eed90bc29
Create Date: 2026-08-19 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision: str = "c4f1a2b3d4e5"
down_revision: Union[str, Sequence[str], None] = "8b3eed90bc29"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

VALID_STATUSES = (
    "Applied",
    "Interview",
    "Offer",
    "Accepted",
    "Rejected",
    "Withdrawn",
)


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
        inspector = inspect(bind)
        tables = inspector.get_table_names()

    user_columns = {col["name"] for col in inspector.get_columns("users")}
    if "token_version" not in user_columns:
        op.add_column(
            "users",
            sa.Column(
                "token_version",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
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

    job_columns = {col["name"] for col in inspector.get_columns("jobs")}
    if "user_id" not in job_columns:
        op.add_column(
            "jobs",
            sa.Column("user_id", sa.Integer(), nullable=True),
        )
        orphan_count = bind.execute(
            text("SELECT COUNT(*) FROM jobs WHERE user_id IS NULL")
        ).scalar()
        if orphan_count:
            raise RuntimeError(
                f"Refusing to continue: {orphan_count} job(s) have no user_id. "
                "Assign each row a valid users.id, then re-run "
                "`alembic upgrade head`. Jobs were not deleted."
            )
        op.alter_column("jobs", "user_id", nullable=False)

        fks = {fk["name"] for fk in inspector.get_foreign_keys("jobs")}
        if "fk_jobs_user_id_users" not in fks:
            op.create_foreign_key(
                "fk_jobs_user_id_users",
                "jobs",
                "users",
                ["user_id"],
                ["id"],
            )

    inspector = inspect(bind)
    indexes = {idx["name"] for idx in inspector.get_indexes("jobs")}
    if "idx_jobs_user_id" not in indexes:
        op.create_index("idx_jobs_user_id", "jobs", ["user_id"])
    if "idx_jobs_company" not in indexes:
        op.create_index("idx_jobs_company", "jobs", ["company"])
    if "idx_jobs_status" not in indexes:
        op.create_index("idx_jobs_status", "jobs", ["status"])

    for canonical in VALID_STATUSES:
        bind.execute(
            text(
                "UPDATE jobs SET status = :canonical "
                "WHERE lower(status) = lower(:canonical)"
            ),
            {"canonical": canonical},
        )

    allowed = ", ".join(f"'{value}'" for value in VALID_STATUSES)
    invalid = bind.execute(
        text(
            f"SELECT DISTINCT status FROM jobs "
            f"WHERE status IS NULL OR status NOT IN ({allowed})"
        )
    ).fetchall()
    if invalid:
        values = ", ".join(repr(row[0]) for row in invalid)
        raise RuntimeError(
            "Refusing to rewrite unknown job status values: "
            f"{values}. Update them to one of {VALID_STATUSES}, "
            "then re-run `alembic upgrade head`."
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "users" in inspector.get_table_names():
        columns = {col["name"] for col in inspector.get_columns("users")}
        if "token_version" in columns:
            op.drop_column("users", "token_version")
