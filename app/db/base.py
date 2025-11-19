"""Database base configuration."""
from advanced_alchemy import SQLAlchemyAsyncRepository
from advanced_alchemy.base import UUIDAuditBase, BigIntAuditBase
from advanced_alchemy.extensions.litestar import (
    AlembicAsyncConfig,
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
)
from litestar.contrib.sqlalchemy import init_plugin_config

from app.config import settings

db_config = SQLAlchemyAsyncConfig(
    connection_string=settings.database_url,
    session_config=AsyncSessionConfig(expire_on_commit=False),
    alembic_config=AlembicAsyncConfig(
        version_table_name="alembic_version",
        script_config=dict(
            alembic=dict(
                script_location="app/db/migrations",
                version_path_separator="os",
            ),
        ),
    ),
)

sqlalchemy_config = init_plugin_config(db_config)

# Base classes
Base = BigIntAuditBase


class Repository(SQLAlchemyAsyncRepository):
    """Base repository."""

    model_type = Base


async def get_session():
    """Get database session."""
    async with db_config.get_session() as session:
        yield session

