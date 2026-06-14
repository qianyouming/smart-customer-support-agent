"""Database engine, session factory, and lightweight SQLite migrations."""

from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.models import Base


def _ensure_sqlite_parent() -> None:
    """Create the local data directory before SQLite opens the database file."""
    if not settings.database_url.startswith("sqlite:///"):
        return
    raw_path = settings.database_url.replace("sqlite:///", "", 1)
    Path(raw_path).parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_parent()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create tables and apply compatibility migrations."""
    Base.metadata.create_all(bind=engine)
    _migrate_sqlite_sessions()


def get_db_session() -> Session:
    """Return a new SQLAlchemy session after ensuring the schema exists."""
    init_db()
    return SessionLocal()


def _migrate_sqlite_sessions() -> None:
    """Add columns introduced after the initial demo database was created."""
    if not settings.database_url.startswith("sqlite"):
        return
    inspector = inspect(engine)
    if "sessions" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("sessions")}
    with engine.begin() as conn:
        if "title" not in columns:
            conn.execute(text("ALTER TABLE sessions ADD COLUMN title VARCHAR(120)"))
        if "is_test" not in columns:
            conn.execute(text("ALTER TABLE sessions ADD COLUMN is_test BOOLEAN DEFAULT 0"))
