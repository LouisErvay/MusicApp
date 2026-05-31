from __future__ import annotations

from fastapi import FastAPI

from src.ORM.database import get_health


app = FastAPI(title="File Browser API")

@app.get("/health")
def health():
    return {"status": "ok", "db": get_health()}

