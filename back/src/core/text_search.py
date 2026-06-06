from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.sql.elements import ColumnElement


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def ilike_unaccent(column: ColumnElement, term: str) -> ColumnElement:
    """Recherche partielle insensible à la casse et aux accents (PostgreSQL unaccent)."""
    pattern = f"%{_escape_like(term)}%"
    return func.unaccent(column).ilike(func.unaccent(pattern), escape="\\")
