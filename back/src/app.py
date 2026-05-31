from __future__ import annotations

from fastapi import FastAPI

from src.ORM import database
from src.ORM.database import get_health, get_session

from fastapi_files import FilesEndpoint, register_plugin
from fastapi import UploadFile
from sqlalchemy.orm import Session
from fastapi import Depends

app = FastAPI(title="File Browser API")

database._ensure_session_factory()

plugin = register_plugin(
    app,
    session_factory=database.SessionLocal,
    volume="./data/files",
    prefix="/files",
    endpoints="all",
    max_upload_size=50 * 1024 * 1024,
    auto_migrate=True,
)

@app.post("/documents")
def create_document(file: UploadFile, session: Session = Depends(get_session)):
    return plugin.api.upload(
        session,
        filename=file.filename,
        stream=file.file,
        mime=file.content_type,
    )

@app.get("/health")
def health():
    return {"status": "ok", "db": get_health()}

