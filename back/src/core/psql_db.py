"""Moteur SQLAlchemy et sessions."""
from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.core.config import config

_engine = None
SessionLocal = None


class Base(DeclarativeBase):
    pass

def get_health():
    """Retourne le statut de la base de données."""
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        return False
    return True

def _build_engine():
    """Construit l'engin SQLAlchemy."""
    return create_engine(config.sqlalchemy_psql_db_url, pool_pre_ping=True, future=True)


def get_engine():
    """Retourne l'instance de l'engin SQLAlchemy."""
    global _engine
    if _engine is None:
        _engine = _build_engine()
    return _engine


def reset_engine_for_tests():
    """Réinitialise le moteur (tests uniquement)."""
    global _engine, SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    SessionLocal = None


def _ensure_session_factory():
    """Assure que la factory de sessions est initialisée."""
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = sessionmaker(
            bind=get_engine(), autocommit=False, autoflush=False, class_=Session, future=True
        )


def init_db():
    """Crée les tables si besoin."""

    _ensure_session_factory()
    Base.metadata.create_all(bind=get_engine())


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Crée une session SQLAlchemy."""
    _ensure_session_factory()
    assert SessionLocal is not None
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency (sync)."""
    _ensure_session_factory()
    assert SessionLocal is not None
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
