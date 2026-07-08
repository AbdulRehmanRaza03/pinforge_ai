"""
database.py
SQLAlchemy engine + session management. SQLite by default, swap DATABASE_URL
to a Postgres URL (e.g. postgresql://user:pass@host/db) for production.
"""

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import Config

connect_args = {"check_same_thread": False} if Config.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(Config.DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def init_db():
    """Create all tables. Call once at app startup."""
    import models  # noqa: F401 ensures models are registered on Base
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session():
    """Context-managed DB session: `with get_session() as db: ...`"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
