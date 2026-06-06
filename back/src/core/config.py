from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]  # back/src -> back
ENV_FILE = BASE_DIR / ".env"

# Charge back/.env si présent (sans écraser les variables déjà définies)
load_dotenv(ENV_FILE, override=False)


def _env(key: str, default: str | None = None) -> str | None:
    value = os.getenv(key, default)
    return value


@dataclass(frozen=True)
class Config:
    API_PORT: int = int(_env("API_PORT", "8000") or 8000)
    API_URL: str = _env("API_URL", f"http://localhost:{API_PORT}") or f"http://localhost:{API_PORT}"

    POSTGRES_URL: str | None = _env("POSTGRES_URL")
    POSTGRES_USER: str = _env("POSTGRES_USER", "postgres") or "postgres"
    POSTGRES_PASSWORD: str = _env("POSTGRES_PASSWORD", "postgres") or "postgres"
    POSTGRES_DB: str = _env("POSTGRES_DB", "postgres") or "postgres"
    POSTGRES_PORT: int = int(_env("POSTGRES_PORT", "5432") or 5432)
    POSTGRES_HOST: str = _env("POSTGRES_HOST", "localhost") or "localhost"

    @property
    def sqlalchemy_psql_db_url(self) -> str:
        """
        Retourne une URL compatible SQLAlchemy.
        - Accepte POSTGRES_URL si déjà au bon format.
        - Si POSTGRES_URL est au format http(s)://..., on reconstruit une URL postgres.
        """
        if self.POSTGRES_URL:
            if self.POSTGRES_URL.startswith("postgresql://") or self.POSTGRES_URL.startswith("postgresql+psycopg2://"):
                return self.POSTGRES_URL
            if self.POSTGRES_URL.startswith("postgres://"):
                return self.POSTGRES_URL.replace("postgres://", "postgresql://", 1)
            if self.POSTGRES_URL.startswith("http://") or self.POSTGRES_URL.startswith("https://"):
                # .env.example contient http://... mais Postgres attend postgresql://...
                return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            return self.POSTGRES_URL

        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


config = Config()
