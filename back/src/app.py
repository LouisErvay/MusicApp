from __future__ import annotations

from fastapi import FastAPI

from src.core import psql_db
from src.core.migrations import run_app_migrations
from src.core.psql_db import get_health, get_session

from fastapi_files import register_plugin

from src.endpoints.ept_song import build_router


app = FastAPI(title="Music Platform API")

psql_db._ensure_session_factory()

plugin = register_plugin(
    app,
    session_factory=psql_db.SessionLocal,
    volume="./data/files",
    prefix="/files",
    endpoints="all",
    max_upload_size=50 * 1024 * 1024,
    auto_migrate=True,
)
run_app_migrations(psql_db.get_engine())

app.include_router(build_router(plugin.api))

@app.get("/health")
def health():
    return {"status": "ok", "db": get_health()}

