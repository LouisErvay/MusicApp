from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ArtistCreate(BaseModel):
    username: str = Field(min_length=1, max_length=100)


class ArtistUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=100)


class ArtistRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    updated_at: datetime


class ArtistPage(BaseModel):
    items: list[ArtistRead]
    total: int
    page: int
    size: int
    pages: int
