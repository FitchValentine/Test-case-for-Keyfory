"""User controller."""
from typing import List

from advanced_alchemy.extensions.litestar import SQLAlchemyAsyncRepository
from litestar import Controller, delete, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.logger import get_logger, trace_id_context
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user import UserService

logger = get_logger(__name__)


async def get_user_service(session: AsyncSession = Provide(get_session)) -> UserService:
    """Dependency for user service."""
    return UserService(session=session)


class UserController(Controller):
    """User controller."""

    path = "/users"
    tags = ["Users"]
    dependencies = {"service": Provide(get_user_service)}

    @post(
        "/",
        status_code=HTTP_201_CREATED,
        summary="Create user",
        description="Create a new user",
    )
    async def create_user(
        self, data: UserCreate, service: UserService
    ) -> UserResponse:
        """Create a new user."""
        try:
            user = await service.create_user(data)
            
            # Publish event to RabbitMQ
            from app.rabbitmq.producer import publish_user_event
            await publish_user_event("user.created", {"user_id": user.id, "name": user.name})
            
            return UserResponse(
                id=user.id,
                name=user.name,
                surname=user.surname,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
        except Exception as e:
            logger.error("error_creating_user", error=str(e), exc_info=True)
            raise HTTPException(detail=str(e)) from e

    @get(
        "/",
        summary="Get users",
        description="Get list of users",
    )
    async def get_users(
        self, service: UserService, skip: int = 0, limit: int = 100
    ) -> List[UserResponse]:
        """Get list of users."""
        try:
            users = await service.get_users(skip=skip, limit=limit)
            return [
                UserResponse(
                    id=user.id,
                    name=user.name,
                    surname=user.surname,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                )
                for user in users
            ]
        except Exception as e:
            logger.error("error_getting_users", error=str(e), exc_info=True)
            raise HTTPException(detail=str(e)) from e

    @get(
        "/{user_id:int}",
        summary="Get user",
        description="Get user by ID",
    )
    async def get_user(self, user_id: int, service: UserService) -> UserResponse:
        """Get user by ID."""
        try:
            user = await service.get_user(user_id)
            return UserResponse(
                id=user.id,
                name=user.name,
                surname=user.surname,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
        except Exception as e:
            logger.error("error_getting_user", user_id=user_id, error=str(e), exc_info=True)
            raise HTTPException(detail=str(e)) from e

    @put(
        "/{user_id:int}",
        summary="Update user",
        description="Update user by ID",
    )
    async def update_user(
        self, user_id: int, data: UserUpdate, service: UserService
    ) -> UserResponse:
        """Update user."""
        try:
            user = await service.update_user(user_id, data)
            
            # Publish event to RabbitMQ
            from app.rabbitmq.producer import publish_user_event
            await publish_user_event("user.updated", {"user_id": user.id, "name": user.name})
            
            return UserResponse(
                id=user.id,
                name=user.name,
                surname=user.surname,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
        except Exception as e:
            logger.error("error_updating_user", user_id=user_id, error=str(e), exc_info=True)
            raise HTTPException(detail=str(e)) from e

    @delete(
        "/{user_id:int}",
        status_code=HTTP_204_NO_CONTENT,
        summary="Delete user",
        description="Delete user by ID",
    )
    async def delete_user(self, user_id: int, service: UserService) -> None:
        """Delete user."""
        try:
            await service.delete_user(user_id)
            
            # Publish event to RabbitMQ
            from app.rabbitmq.producer import publish_user_event
            await publish_user_event("user.deleted", {"user_id": user_id})
        except Exception as e:
            logger.error("error_deleting_user", user_id=user_id, error=str(e), exc_info=True)
            raise HTTPException(detail=str(e)) from e

