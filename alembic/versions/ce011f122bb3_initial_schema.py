"""initial schema

Revision ID: ce011f122bb3
Revises:
Create Date: 2026-07-09 00:21:46.022075

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ce011f122bb3"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade():
    op.create_table(
        "entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("chat_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
    )
    op.create_table(
        "user_settings",
        sa.Column("chat_id", sa.String(), primary_key=True),
        sa.Column("language", sa.String(), nullable=False, server_default="en"),
        sa.Column("currency", sa.String(), nullable=False, server_default="PLN"),
    )


def downgrade():
    op.drop_table("user_settings")
    op.drop_table("entries")
