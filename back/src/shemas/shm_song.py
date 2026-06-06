from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import IO

from fastapi_files.schemas import FileRead
from pydantic import BaseModel, ConfigDict, Field


@dataclass
class SongCreate:
    """Entrée service : nom de la chanson + flux binaire du fichier audio."""

    name: str
    filename: str
    stream: IO[bytes]
    mime: str | None = None
    artist_names: list[str] | None = None
    tag_names: list[str] | None = None


class SongUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)


class SongRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    file_id: uuid.UUID
    updated_at: datetime
    file: FileRead | None = None


class SongPage(BaseModel):
    items: list[SongRead]
    total: int
    page: int
    size: int
    pages: int


class SongBulkCreateItem(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    file_index: int = Field(ge=0)
    artist: list[str] = Field(default_factory=list)
    tag: list[str] = Field(default_factory=list)


class SongBulkRead(BaseModel):
    items: list[SongRead]
    created: int
