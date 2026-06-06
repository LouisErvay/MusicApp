from __future__ import annotations

from fastapi_files import FileNotFound, FilesAPI
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.mod_song import Song
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


def create(session: Session, files_api: FilesAPI, payload: SongCreate) -> SongRead:
    file = files_api.upload(
        session,
        filename=payload.filename,
        stream=payload.stream,
        mime=payload.mime,
    )
    song = Song(name=payload.name, file_id=file.id)
    session.add(song)
    session.flush()
    return _to_read(session, files_api, song)


def list_songs(
    session: Session, files_api: FilesAPI, *, page: int, size: int
) -> SongPage:
    total = session.scalar(select(func.count()).select_from(Song)) or 0
    offset = (page - 1) * size
    songs = list(
        session.scalars(select(Song).order_by(Song.id).offset(offset).limit(size))
    )
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
