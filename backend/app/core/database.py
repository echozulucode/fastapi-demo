"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings

_is_sqlite = "sqlite" in settings.DATABASE_URL

_engine_kwargs: dict = {
    "echo": settings.ENVIRONMENT == "development",
}

if _is_sqlite:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    _engine_kwargs.update(
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)


def create_db_and_tables() -> None:
    """Create all database tables (skips existing ones)."""
    from app.models.base import Base
    Base.metadata.create_all(engine, checkfirst=True)


def get_session():
    """Yield a database session; automatically closed when the request ends."""
    with Session(engine) as session:
        yield session
