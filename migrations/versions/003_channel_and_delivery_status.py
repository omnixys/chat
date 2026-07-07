"""add channel and delivery_status to messages

Revision ID: 003
Revises: 002
Create Date: 2026-07-07
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "messages",
        sa.Column("channel", sa.String(20), nullable=False, server_default="IN_APP"),
    )
    op.add_column(
        "messages",
        sa.Column("delivery_status", sa.String(20), nullable=False, server_default="PENDING"),
    )


def downgrade() -> None:
    op.drop_column("messages", "delivery_status")
    op.drop_column("messages", "channel")
