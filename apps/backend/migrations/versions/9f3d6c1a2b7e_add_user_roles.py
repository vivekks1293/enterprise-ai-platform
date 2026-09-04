"""add user roles

Revision ID: 9f3d6c1a2b7e
Revises: f033dd9cfcfe
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9f3d6c1a2b7e"
down_revision: Union[str, Sequence[str], None] = "f033dd9cfcfe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role_type", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "users",
        sa.Column(
            "role_type_name",
            sa.String(length=20),
            nullable=False,
            server_default="user",
        ),
    )
    op.alter_column("users", "role_type", server_default=None)
    op.alter_column("users", "role_type_name", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "role_type_name")
    op.drop_column("users", "role_type")