"""User schemas."""
from datetime import datetime

from msgspec import Struct


class UserBase(Struct):
    """Base user schema."""

    name: str
    surname: str


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str


class UserUpdate(Struct):
    """Schema for updating a user."""

    name: str | None = None
    surname: str | None = None
    password: str | None = None


class UserResponse(UserBase):
    """Schema for user response."""

    id: int
    created_at: datetime
    updated_at: datetime

