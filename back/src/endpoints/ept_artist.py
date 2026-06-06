from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.core.psql_db import get_session
from src.services import svc_artist
from src.services.svc_artist import ArtistAlreadyExists, ArtistNotFound
from src.shemas.shm_artist import ArtistCreate, ArtistPage, ArtistRead, ArtistUpdate


router = APIRouter(prefix="/artists", tags=["artists"])


@router.post("/", response_model=ArtistRead, status_code=status.HTTP_201_CREATED)
def create_artist(
    payload: ArtistCreate,
    session: Session = Depends(get_session),
) -> ArtistRead:
    try:
        return svc_artist.create(session, payload)
    except ArtistAlreadyExists as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc


@router.get("/", response_model=ArtistPage)
def list_artists(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> ArtistPage:
    return svc_artist.list_artists(session, page=page, size=size)


@router.get("/{artist_id}", response_model=ArtistRead)
def get_artist(artist_id: int, session: Session = Depends(get_session)) -> ArtistRead:
    try:
        return svc_artist.get(session, artist_id)
    except ArtistNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.patch("/{artist_id}", response_model=ArtistRead)
def update_artist(
    artist_id: int,
    payload: ArtistUpdate,
    session: Session = Depends(get_session),
) -> ArtistRead:
    try:
        return svc_artist.update(session, artist_id, payload)
    except ArtistNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except ArtistAlreadyExists as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc


@router.delete("/{artist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_artist(artist_id: int, session: Session = Depends(get_session)) -> None:
    try:
        svc_artist.delete(session, artist_id)
    except ArtistNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
