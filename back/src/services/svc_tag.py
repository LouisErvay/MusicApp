from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.core.text_search import ilike_unaccent
from src.models.mod_tag import Tag
from src.shemas.shm_tag import TagCreate, TagPage, TagRead, TagUpdate


class TagNotFound(Exception):
    pass


class TagAlreadyExists(Exception):
    pass


def _require(session: Session, tag_id: int) -> Tag:
    tag = session.get(Tag, tag_id)
    if tag is None:
        raise TagNotFound(f"Tag inconnu : {tag_id}")
    return tag


def get_or_create(session: Session, name: str) -> Tag:
    tag = session.scalar(select(Tag).where(Tag.name == name))
    if tag is not None:
        return tag
    tag = Tag(name=name)
    session.add(tag)
    session.flush()
    return tag


def create(session: Session, payload: TagCreate) -> TagRead:
    tag = Tag(name=payload.name)
    session.add(tag)
    try:
        session.flush()
    except IntegrityError as exc:
        raise TagAlreadyExists(f"Tag déjà existant : {payload.name}") from exc
    return TagRead.model_validate(tag)


def list_tags(session: Session, *, page: int, size: int, name: str | None = None) -> TagPage:
    stmt = select(Tag)
    if name:
        stmt = stmt.where(ilike_unaccent(Tag.name, name))
    total = session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    offset = (page - 1) * size
    tags = list(session.scalars(stmt.order_by(Tag.id).offset(offset).limit(size)))
    pages = (total + size - 1) // size if total > 0 else 0
    return TagPage(
        items=[TagRead.model_validate(tag) for tag in tags],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


def get(session: Session, tag_id: int) -> TagRead:
    return TagRead.model_validate(_require(session, tag_id))


def update(session: Session, tag_id: int, payload: TagUpdate) -> TagRead:
    tag = _require(session, tag_id)
    if payload.name is not None:
        tag.name = payload.name
    session.add(tag)
    try:
        session.flush()
    except IntegrityError as exc:
        raise TagAlreadyExists(f"Tag déjà existant : {payload.name}") from exc
    return TagRead.model_validate(tag)


def delete(session: Session, tag_id: int) -> None:
    tag = _require(session, tag_id)
    session.delete(tag)
    session.flush()
