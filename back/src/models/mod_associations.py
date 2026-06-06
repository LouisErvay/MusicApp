from sqlalchemy import Column, ForeignKey, Integer, Table

from src.core.psql_db import Base

song_artist = Table(
    "song_artist",
    Base.metadata,
    Column(
        "song_id",
        Integer,
        ForeignKey("song.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "artist_id",
        Integer,
        ForeignKey("artist.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

song_tag = Table(
    "song_tag",
    Base.metadata,
    Column(
        "song_id",
        Integer,
        ForeignKey("song.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("tag.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
