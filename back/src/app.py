from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_files.config import FilesEndpoint

from src.core import psql_db
from src.core.migrations import run_app_migrations
from src.core.psql_db import get_health, get_session

from fastapi_files import register_plugin

from src.endpoints import ept_artist, ept_tag
from src.endpoints.ept_song import build_router


app = FastAPI(title="Music Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

psql_db._ensure_session_factory()

plugin = register_plugin(
    app,
    session_factory=psql_db.SessionLocal,
    volume="./data/files",
    prefix="/files",
    max_upload_size=50 * 1024 * 1024,
    auto_migrate=True,
    endpoints=[FilesEndpoint.DOWNLOAD],
)
run_app_migrations(psql_db.get_engine())

app.include_router(build_router(plugin.api))
app.include_router(ept_artist.router)
app.include_router(ept_tag.router)

@app.get("/health")
def health():
    return {"status": "ok", "db": get_health()}

