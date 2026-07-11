"""convert created_at to datetime

Revision ID: 568a82c0abc4
Revises: ce011f122bb3
Create Date: 2026-07-11 11:23:53.006365

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "568a82c0abc4"
down_revision: str | Sequence[str] | None = "ce011f122bb3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "entries",
        "created_at",
        existing_type=sa.String(),
        type_=sa.DateTime(),
        postgresql_using="created_at::timestamp",
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "entries",
        "created_at",
        existing_type=sa.DateTime(),
        type_=sa.String(),
        postgresql_using="created_at::text",
        existing_nullable=False,
    )
