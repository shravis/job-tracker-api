"""Force-add users.token_version (idempotent).

This revision was applied on existing databases after d5e6f7a8b9c0
did not add the column. Do not delete it — collapsing already-applied
revisions rewrites history. ADD COLUMN IF NOT EXISTS is a no-op when
the column is already present.

Revision ID: e7f8a9b0c1d2
Revises: d5e6f7a8b9c0
Create Date: 2026-08-19 20:16:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "e7f8a9b0c1d2"
down_revision: Union[str, Sequence[str], None] = "d5e6f7a8b9c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users "
        "ADD COLUMN IF NOT EXISTS token_version INTEGER NOT NULL DEFAULT 0"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS token_version")
