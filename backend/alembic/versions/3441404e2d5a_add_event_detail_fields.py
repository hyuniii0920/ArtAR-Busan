"""add event detail fields

Revision ID: 3441404e2d5a
Revises: 26941c46d243
Create Date: 2026-06-06 01:17:36.697998

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3441404e2d5a'
down_revision: Union[str, None] = '26941c46d243'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("event", sa.Column("exhibition_hall_name", sa.String(length=200), nullable=True))
    op.add_column("event", sa.Column("location", sa.String(length=500), nullable=True))
    op.add_column("event", sa.Column("organizer_name", sa.String(length=200), nullable=True))
    op.add_column("event", sa.Column("memo", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("event", "memo")
    op.drop_column("event", "organizer_name")
    op.drop_column("event", "location")
    op.drop_column("event", "exhibition_hall_name")
