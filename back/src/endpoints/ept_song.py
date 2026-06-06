from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi_files import FileNotFound, FileTooLarge, FilesAPI
from sqlalchemy.orm import Session

from src.core.psql_db import get_session
from src.services import svc_song
from src.services.svc_song import SongNotFound
from src.shemas.shm_song import SongCreate, SongPage, SongRead, SongUpdate


def build_router(files_api: FilesAPI) -> APIRouter:
    router = APIRouter(prefix="/songs", tags=["songs"])

    @router.post("/", response_model=SongRead, status_code=status.HTTP_201_CREATED)
    def create_song(
        name: str = Form(..., min_length=1, max_length=100),
        file: UploadFile = File(...),
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
                ),
            )
        except FileTooLarge as exc:
            raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, str(exc)) from exc

    @router.get("/", response_model=SongPage)
    def list_songs(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        session: Session = Depends(get_session),
    ) -> SongPage:
        return svc_song.list_songs(session, files_api, page=page, size=size)

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
