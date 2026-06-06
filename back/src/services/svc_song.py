from __future__ import annotations

from fastapi_files import FileNotFound, FilesAPI
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.core.text_search import ilike_unaccent
from src.models.mod_artist import Artist
from src.models.mod_song import Song
from src.models.mod_tag import Tag
from src.services import svc_artist, svc_tag
from src.shemas.shm_song import SongCreate, SongPage, SongRead, SongUpdate


class SongNotFound(Exception):
    pass


def _require(session: Session, song_id: int) -> Song:
    song = session.get(Song, song_id)
    if song is None:
        raise SongNotFound(f"Chanson inconnue : {song_id}")
    return song


def _to_read(session: Session, files_api: FilesAPI, song: Song) -> SongRead:
    file = files_api.get_file(session, song.file_id)
    return SongRead.model_validate(song).model_copy(update={"file": file})


def _normalize_names(names: list[str] | None) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for name in names or []:
        cleaned = name.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
    return result


def create(session: Session, files_api: FilesAPI, payload: SongCreate) -> SongRead:
    file = files_api.upload(
        session,
        filename=payload.filename,
        stream=payload.stream,
        mime=payload.mime,
    )
    song = Song(name=payload.name, file_id=file.id)
    for username in _normalize_names(payload.artist_names):
        song.artists.append(svc_artist.get_or_create(session, username))
    for name in _normalize_names(payload.tag_names):
        song.tags.append(svc_tag.get_or_create(session, name))
    session.add(song)
    session.flush()
    return _to_read(session, files_api, song)


def create_bulk(
    session: Session, files_api: FilesAPI, payloads: list[SongCreate]
) -> list[SongRead]:
    return [create(session, files_api, payload) for payload in payloads]


def _song_filters(
    stmt,
    *,
    name: str | None = None,
    artist_ids: list[int],
    tag_ids: list[int],
):
    if name:
        stmt = stmt.where(ilike_unaccent(Song.name, name))
    if artist_ids:
        stmt = stmt.where(Song.artists.any(Artist.id.in_(artist_ids)))
    if tag_ids:
        stmt = stmt.where(Song.tags.any(Tag.id.in_(tag_ids)))
    return stmt


def list_songs(
    session: Session,
    files_api: FilesAPI,
    *,
    page: int,
    size: int,
    name: str | None = None,
    artist_ids: list[int] | None = None,
    tag_ids: list[int] | None = None,
) -> SongPage:
    artist_ids = artist_ids or []
    tag_ids = tag_ids or []
    count_stmt = _song_filters(
        select(func.count()).select_from(Song),
        name=name,
        artist_ids=artist_ids,
        tag_ids=tag_ids,
    )
    total = session.scalar(count_stmt) or 0
    offset = (page - 1) * size
    songs_stmt = _song_filters(
        select(Song).order_by(Song.id),
        name=name,
        artist_ids=artist_ids,
        tag_ids=tag_ids,
    )
    songs = list(session.scalars(songs_stmt.offset(offset).limit(size)))
    pages = (total + size - 1) // size if total > 0 else 0
    return SongPage(
        items=[_to_read(session, files_api, song) for song in songs],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


def get(session: Session, files_api: FilesAPI, song_id: int) -> SongRead:
    return _to_read(session, files_api, _require(session, song_id))


def update(
    session: Session, files_api: FilesAPI, song_id: int, payload: SongUpdate
) -> SongRead:
    song = _require(session, song_id)
    if payload.name is not None:
        song.name = payload.name
    session.add(song)
    session.flush()
    return _to_read(session, files_api, song)


def delete(session: Session, files_api: FilesAPI, song_id: int) -> None:
    song = _require(session, song_id)
    file_id = song.file_id
    session.delete(song)
    session.flush()
    try:
        files_api.delete_file(session, file_id)
    except FileNotFound:
        pass
