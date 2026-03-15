"""Alembic migration environment."""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Make the app package importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Alembic Config object
config = context.config

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models so Alembic can detect tables for autogenerate
from app.models.base import Base  # noqa: E402
from app.models.user import User  # noqa: E402, F401
from app.models.item import Item  # noqa: E402, F401
from app.models.token import PersonalAccessToken  # noqa: E402, F401

target_metadata = Base.metadata

# Override sqlalchemy.url with DATABASE_URL env var when present
def get_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    return config.get_main_option("sqlalchemy.url", "sqlite:///./app.db")


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (generates SQL script)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations with a live DB connection."""
    cfg_section = config.get_section(config.config_ini_section, {})
    cfg_section["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        cfg_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
