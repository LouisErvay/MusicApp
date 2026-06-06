from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.core.psql_db import get_session
from src.services import svc_tag
from src.services.svc_tag import TagAlreadyExists, TagNotFound
from src.shemas.shm_tag import TagCreate, TagPage, TagRead, TagUpdate


router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(
    payload: TagCreate,
    session: Session = Depends(get_session),
) -> TagRead:
    try:
        return svc_tag.create(session, payload)
    except TagAlreadyExists as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc


@router.get("/", response_model=TagPage)
def list_tags(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> TagPage:
    return svc_tag.list_tags(session, page=page, size=size)


@router.get("/{tag_id}", response_model=TagRead)
def get_tag(tag_id: int, session: Session = Depends(get_session)) -> TagRead:
    try:
        return svc_tag.get(session, tag_id)
    except TagNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.patch("/{tag_id}", response_model=TagRead)
def update_tag(
    tag_id: int,
    payload: TagUpdate,
    session: Session = Depends(get_session),
) -> TagRead:
    try:
        return svc_tag.update(session, tag_id, payload)
    except TagNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except TagAlreadyExists as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, session: Session = Depends(get_session)) -> None:
    try:
        svc_tag.delete(session, tag_id)
    except TagNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
