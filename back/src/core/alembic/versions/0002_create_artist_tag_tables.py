"""create artist, tag and association tables

Revision ID: 0002_create_artist_tag
Revises: 0001_create_song
Create Date: 2026-06-06
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_create_artist_tag"
down_revision: Union[str, None] = "0001_create_song"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "artist",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "tag",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "song_artist",
        sa.Column("song_id", sa.Integer(), nullable=False),
        sa.Column("artist_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["song_id"], ["song.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["artist_id"], ["artist.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("song_id", "artist_id"),
    )
    op.create_table(
        "song_tag",
        sa.Column("song_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["song_id"], ["song.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tag.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("song_id", "tag_id"),
    )


def downgrade() -> None:
    op.drop_table("song_tag")
    op.drop_table("song_artist")
    op.drop_table("tag")
    op.drop_table("artist")
