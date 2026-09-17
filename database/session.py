from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import get_settings
from database.models import Base


def get_engine(url: str | None = None) -> Engine:
    db_url = url or get_settings().database_url
    if db_url.startswith("sqlite"):
        Path("data").mkdir(parents=True, exist_ok=True)
        return create_engine(db_url, connect_args={"check_same_thread": False}, future=True)
    return create_engine(db_url, pool_pre_ping=True, future=True)


def init_db(url: str | None = None) -> Engine:
    engine = get_engine(url)
    Base.metadata.create_all(engine)
    return engine


@contextmanager
def get_session(url: str | None = None) -> Iterator[Session]:
    engine = init_db(url)
    factory = sessionmaker(engine, expire_on_commit=False, future=True)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
