from __future__ import annotations

from fastapi import FastAPI

from src.orm import database
from src.orm.database import get_health, get_session

from fastapi_files import register_plugin


app = FastAPI(title="Music Platform API")

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

@app.get("/health")
def health():
    return {"status": "ok", "db": get_health()}

