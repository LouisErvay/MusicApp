"""enable unaccent extension for accent-insensitive search

Revision ID: 0003_enable_unaccent
Revises: 0002_create_artist_tag
Create Date: 2026-06-06
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0003_enable_unaccent"
down_revision: Union[str, None] = "0002_create_artist_tag"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS unaccent")
