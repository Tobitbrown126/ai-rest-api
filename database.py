"""
database.py
-----------
SQLAlchemy engine, session factory, and declarative base.

Supports both SQLite (default, zero-config local development) and
PostgreSQL (production) via the DATABASE_URL environment variable.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import settings

# ----------------------------------------------------------------------
# Engine configuration
# ----------------------------------------------------------------------
# SQLite requires a special connect_args flag to allow usage across
# multiple threads (FastAPI handles each request in its own thread pool
# for sync dependencies).
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # verify connections before use (important for Postgres)
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""

    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and guarantees
    it is closed after the request completes, even if an exception
    is raised.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Create all tables defined on Base's metadata.

    In production, prefer Alembic migrations (see /alembic) over this
    function. This is primarily useful for local development and tests.
    """
    import models  # noqa: F401  (ensures models are registered on Base.metadata)

    Base.metadata.create_all(bind=engine)
