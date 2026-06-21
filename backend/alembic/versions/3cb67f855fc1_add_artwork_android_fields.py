"""add artwork android fields

Revision ID: 3cb67f855fc1
Revises: 3441404e2d5a
Create Date: 2026-06-21 18:19:03.681308

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '3cb67f855fc1'
down_revision: Union[str, None] = '3441404e2d5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("artwork", sa.Column("code", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_artwork_code"), "artwork", ["code"], unique=True)
    op.add_column(
        "artwork",
        sa.Column("summary_description_i18n", postgresql.JSONB(), server_default="{}", nullable=False),
    )
    op.add_column(
        "artwork",
        sa.Column("detail_description_i18n", postgresql.JSONB(), server_default="{}", nullable=False),
    )
    op.add_column("artwork", sa.Column("image_url", sa.Text(), nullable=True))
    op.add_column("artwork", sa.Column("ar_asset_url", sa.Text(), nullable=True))
    op.add_column("artwork", sa.Column("marker_width_meters", sa.Float(), nullable=True))
    op.alter_column("artwork", "venue_id", existing_type=sa.Uuid(), nullable=True)


def downgrade() -> None:
    op.alter_column("artwork", "venue_id", existing_type=sa.Uuid(), nullable=False)
    op.drop_column("artwork", "marker_width_meters")
    op.drop_column("artwork", "ar_asset_url")
    op.drop_column("artwork", "image_url")
    op.drop_column("artwork", "detail_description_i18n")
    op.drop_column("artwork", "summary_description_i18n")
    op.drop_index(op.f("ix_artwork_code"), table_name="artwork")
    op.drop_column("artwork", "code")
