import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.config import settings
from app.db.database import Base

# Add project root to PYTHONPATH so we can import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --------------------
# Alembic Configuration
# --------------------
config = context.config

# Set SQLAlchemy URL from .env via settings.py
DATABASE_URL = (
    f"postgresql+psycopg2://{settings.database_username}:{settings.database_password}"
    f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
)
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate (e.g. for migrations)
target_metadata = Base.metadata


# --------------------
# Migration Runners
# --------------------


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no DB connection)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (with DB connection)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # helps detect column type changes
        )
        with context.begin_transaction():
            context.run_migrations()


# --------------------
# Entry Point
# --------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
