from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.mod_artist import Artist
from src.shemas.shm_artist import ArtistCreate, ArtistPage, ArtistRead, ArtistUpdate


class ArtistNotFound(Exception):
    pass


class ArtistAlreadyExists(Exception):
    pass


def _require(session: Session, artist_id: int) -> Artist:
    artist = session.get(Artist, artist_id)
    if artist is None:
        raise ArtistNotFound(f"Artiste inconnu : {artist_id}")
    return artist


def get_or_create(session: Session, username: str) -> Artist:
    artist = session.scalar(select(Artist).where(Artist.username == username))
    if artist is not None:
        return artist
    artist = Artist(username=username)
    session.add(artist)
    session.flush()
    return artist


def create(session: Session, payload: ArtistCreate) -> ArtistRead:
    artist = Artist(username=payload.username)
    session.add(artist)
    try:
        session.flush()
    except IntegrityError as exc:
        raise ArtistAlreadyExists(f"Nom d'utilisateur déjà pris : {payload.username}") from exc
    return ArtistRead.model_validate(artist)


def list_artists(session: Session, *, page: int, size: int) -> ArtistPage:
    total = session.scalar(select(func.count()).select_from(Artist)) or 0
    offset = (page - 1) * size
    artists = list(
        session.scalars(select(Artist).order_by(Artist.id).offset(offset).limit(size))
    )
    pages = (total + size - 1) // size if total > 0 else 0
    return ArtistPage(
        items=[ArtistRead.model_validate(artist) for artist in artists],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


def get(session: Session, artist_id: int) -> ArtistRead:
    return ArtistRead.model_validate(_require(session, artist_id))


def update(session: Session, artist_id: int, payload: ArtistUpdate) -> ArtistRead:
    artist = _require(session, artist_id)
    if payload.username is not None:
        artist.username = payload.username
    session.add(artist)
    try:
        session.flush()
    except IntegrityError as exc:
        raise ArtistAlreadyExists(f"Nom d'utilisateur déjà pris : {payload.username}") from exc
    return ArtistRead.model_validate(artist)


def delete(session: Session, artist_id: int) -> None:
    artist = _require(session, artist_id)
    session.delete(artist)
    session.flush()
