"""Normalize job status casing and add a CHECK constraint.

Revision ID: f9a0b1c2d3e4
Revises: e7f8a9b0c1d2
Create Date: 2026-08-20 11:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect, text


revision: str = "f9a0b1c2d3e4"
down_revision: Union[str, Sequence[str], None] = "e7f8a9b0c1d2"
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

    if "jobs" not in inspector.get_table_names():
        return

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
            "Refusing to add jobs.status CHECK constraint; unknown values: "
            f"{values}. Update them to one of {VALID_STATUSES}, "
            "then re-run `alembic upgrade head`."
        )

    checks = {c["name"] for c in inspector.get_check_constraints("jobs")}
    if "ck_jobs_status" not in checks:
        op.create_check_constraint(
            "ck_jobs_status",
            "jobs",
            "status IN ('Applied', 'Interview', 'Offer', 'Accepted', "
            "'Rejected', 'Withdrawn')",
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "jobs" not in inspector.get_table_names():
        return

    checks = {c["name"] for c in inspector.get_check_constraints("jobs")}
    if "ck_jobs_status" in checks:
        op.drop_constraint("ck_jobs_status", "jobs", type_="check")
