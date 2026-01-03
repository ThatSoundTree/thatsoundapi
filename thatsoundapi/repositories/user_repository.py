from sqlalchemy import select

from thatsoundapi.core.exceptions import DatabaseError
from thatsoundapi.db.connection import db_session
from thatsoundapi.db.models import User


class UserRepository:
    """User database operations."""

    @staticmethod
    async def get_by_htelegram_id(hgramid: str) -> User | None:
        """Get user by hashed Telegram ID."""
        session = db_session.get()
        if session is None:
            raise DatabaseError("Database session not found in context")

        result = await session.execute(
            select(User).where(User.hgramid == hgramid),
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(hgramid: str) -> User:
        """Create a new user."""
        session = db_session.get()
        if session is None:
            raise DatabaseError("Database session not found in context")

        user = User(hgramid=hgramid)
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user
