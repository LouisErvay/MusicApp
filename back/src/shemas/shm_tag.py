from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    updated_at: datetime


class TagPage(BaseModel):
    items: list[TagRead]
    total: int
    page: int
    size: int
    pages: int
