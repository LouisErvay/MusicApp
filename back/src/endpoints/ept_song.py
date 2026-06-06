from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi_files import FileNotFound, FileTooLarge, FilesAPI
from pydantic import TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from src.core.psql_db import get_session
from src.services import svc_song
from src.services.svc_song import SongNotFound
from src.shemas.shm_song import (
    SongBulkCreateItem,
    SongBulkRead,
    SongCreate,
    SongPage,
    SongRead,
    SongUpdate,
)

_song_bulk_items_adapter = TypeAdapter(list[SongBulkCreateItem])


def build_router(files_api: FilesAPI) -> APIRouter:
    router = APIRouter(prefix="/songs", tags=["songs"])

    @router.post("/", response_model=SongRead, status_code=status.HTTP_201_CREATED)
    def create_song(
        name: str = Form(..., min_length=1, max_length=100),
        file: UploadFile = File(...),
        artist: list[str] = Form(default=[]),
        tag: list[str] = Form(default=[]),
        session: Session = Depends(get_session),
    ) -> SongRead:
        if not file.filename:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Nom de fichier manquant.")
        try:
            return svc_song.create(
                session,
                files_api,
                SongCreate(
                    name=name,
                    filename=file.filename,
                    stream=file.file,
                    mime=file.content_type,
                    artist_names=artist,
                    tag_names=tag,
                ),
            )
        except FileTooLarge as exc:
            raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, str(exc)) from exc

    @router.post("/bulk", response_model=SongBulkRead, status_code=status.HTTP_201_CREATED)
    def create_songs_bulk(
        items: str = Form(..., description="Tableau JSON des chansons à créer."),
        files: list[UploadFile] = File(...),
        session: Session = Depends(get_session),
    ) -> SongBulkRead:
        try:
            parsed_items = _song_bulk_items_adapter.validate_json(items)
        except ValidationError as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc

        if not parsed_items:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Au moins une chanson est requise.")
        if not files:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Au moins un fichier est requis.")

        payloads: list[SongCreate] = []
        for index, item in enumerate(parsed_items):
            if item.file_index >= len(files):
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    f"Chanson {index + 1} : file_index {item.file_index} hors limites.",
                )
            upload = files[item.file_index]
            if not upload.filename:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    f"Chanson {index + 1} : nom de fichier manquant.",
                )
            payloads.append(
                SongCreate(
                    name=item.name,
                    filename=upload.filename,
                    stream=upload.file,
                    mime=upload.content_type,
                    artist_names=item.artist,
                    tag_names=item.tag,
                )
            )

        try:
            created = svc_song.create_bulk(session, files_api, payloads)
        except FileTooLarge as exc:
            raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, str(exc)) from exc

        return SongBulkRead(items=created, created=len(created))

    @router.get("/", response_model=SongPage)
    def list_songs(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        artist_id: list[int] = Query(default=[]),
        tag_id: list[int] = Query(default=[]),
        session: Session = Depends(get_session),
    ) -> SongPage:
        return svc_song.list_songs(
            session,
            files_api,
            page=page,
            size=size,
            artist_ids=artist_id,
            tag_ids=tag_id,
        )

    @router.get("/{song_id}", response_model=SongRead)
    def get_song(song_id: int, session: Session = Depends(get_session)) -> SongRead:
        try:
            return svc_song.get(session, files_api, song_id)
        except SongNotFound as exc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
        except FileNotFound as exc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc

    @router.patch("/{song_id}", response_model=SongRead)
    def update_song(
        song_id: int,
        payload: SongUpdate,
        session: Session = Depends(get_session),
    ) -> SongRead:
        try:
            return svc_song.update(session, files_api, song_id, payload)
        except SongNotFound as exc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc

    @router.delete("/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_song(song_id: int, session: Session = Depends(get_session)) -> None:
        try:
            svc_song.delete(session, files_api, song_id)
        except SongNotFound as exc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc

    return router
