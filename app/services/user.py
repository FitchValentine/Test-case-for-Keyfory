"""User service."""
from typing import List

from advanced_alchemy.extensions.litestar import SQLAlchemyAsyncRepository
from litestar.exceptions import NotFoundException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.logger import get_logger
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate

logger = get_logger(__name__)


class UserService:
    """User service."""

    def __init__(self, session: AsyncSession):
        """Initialize service."""
        self.session = session
        self.repository = UserRepository(session=session)

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        logger.info("creating_user", name=user_data.name, surname=user_data.surname)
        
        user = User(
            name=user_data.name,
            surname=user_data.surname,
            password=user_data.password,  # In production, hash the password
        )
        
        user = await self.repository.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        
        logger.info("user_created", user_id=user.id)
        return user

    async def get_user(self, user_id: int) -> User:
        """Get user by ID."""
        logger.info("getting_user", user_id=user_id)
        
        user = await self.repository.get_one_or_none(id=user_id)
        if not user:
            logger.warning("user_not_found", user_id=user_id)
            raise NotFoundException(f"User with ID {user_id} not found")
        
        return user

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get list of users."""
        logger.info("getting_users", skip=skip, limit=limit)
        
        result = await self.session.execute(
            select(User).offset(skip).limit(limit)
        )
        users = result.scalars().all()
        
        logger.info("users_retrieved", count=len(users))
        return list(users)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user."""
        logger.info("updating_user", user_id=user_id)
        
        user = await self.get_user(user_id)
        
        if user_data.name is not None:
            user.name = user_data.name
        if user_data.surname is not None:
            user.surname = user_data.surname
        if user_data.password is not None:
            user.password = user_data.password  # In production, hash the password
        
        await self.session.commit()
        await self.session.refresh(user)
        
        logger.info("user_updated", user_id=user.id)
        return user

    async def delete_user(self, user_id: int) -> None:
        """Delete user."""
        logger.info("deleting_user", user_id=user_id)
        
        user = await self.get_user(user_id)
        await self.repository.delete(user)
        await self.session.commit()
        
        logger.info("user_deleted", user_id=user_id)

