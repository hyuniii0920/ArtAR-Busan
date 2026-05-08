"""add timestamps and visit_log relationships

Revision ID: dedb65b50f04
Revises: fa50084cc4ef
Create Date: 2026-05-08 19:52:26.654558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'dedb65b50f04'
down_revision: Union[str, None] = 'fa50084cc4ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    now = sa.func.now()

    op.add_column(
        "event_theme",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now, nullable=False),
    )
    op.add_column(
        "event_theme",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now, nullable=False),
    )

    op.add_column(
        "venue",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now, nullable=False),
    )
    op.add_column(
        "venue",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now, nullable=False),
    )

    op.add_column(
        "artwork",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now, nullable=False),
    )


def downgrade() -> None:
    op.drop_column("artwork", "updated_at")
    op.drop_column("venue", "updated_at")
    op.drop_column("venue", "created_at")
    op.drop_column("event_theme", "updated_at")
    op.drop_column("event_theme", "created_at")
