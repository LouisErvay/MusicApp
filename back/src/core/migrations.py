"""Applique les migrations Alembic de l'application."""
from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.engine import Engine

ALEMBIC_DIR = Path(__file__).resolve().parent / "alembic"


def run_app_migrations(engine: Engine, *, revision: str = "head") -> None:
    cfg = Config()
    cfg.set_main_option("script_location", str(ALEMBIC_DIR))
    cfg.attributes["connection"] = engine
    command.upgrade(cfg, revision)
