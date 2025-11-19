"""Alembic environment configuration."""
from advanced_alchemy.extensions.litestar import AlembicAsyncConfig

from app.db.base import db_config

# This file is used by Alembic for migrations
# The actual configuration is in app.db.base.db_config
# Advanced-alchemy will handle the migration setup automatically

