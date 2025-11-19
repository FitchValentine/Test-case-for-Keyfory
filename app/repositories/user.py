"""User repository."""
from advanced_alchemy import SQLAlchemyAsyncRepository

from app.db.models import User


class UserRepository(SQLAlchemyAsyncRepository[User]):
    """User repository."""

    model_type = User

