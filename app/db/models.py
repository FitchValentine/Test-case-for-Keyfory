"""Database models."""
from datetime import datetime

from advanced_alchemy.base import BigIntPrimaryKey
from sqlalchemy import Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """User model."""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigIntPrimaryKey, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    surname: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

