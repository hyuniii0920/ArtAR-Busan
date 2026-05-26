"""add users table

Revision ID: 26941c46d243
Revises: dedb65b50f04
Create Date: 2026-05-26 13:52:10.942702

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '26941c46d243'
down_revision: Union[str, None] = 'dedb65b50f04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("museum_status", sa.String(length=20), nullable=True),
        sa.Column("museum_name", sa.String(length=200), nullable=True),
        sa.Column("contact", sa.String(length=100), nullable=True),
        sa.Column("proof_file_name", sa.String(length=255), nullable=True),
        sa.Column("proof_file_url", sa.String(length=1000), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
