from sqlalchemy import select, insert

from thatsoundapi.utils.exceptions.app import UnknownDatabaseError

from thatsoundapi.db.connection import db_session
from thatsoundapi.db.models import User


class UserRepository:
    """User database operations."""

    @staticmethod
    async def get_by_hgramid(hgramid: str) -> User | None:
        """Get user by hashed Telegram ID."""
        session = db_session.get()
        if session is None:
            raise UnknownDatabaseError

        query = select(User).where(User.hgramid == hgramid)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(hgramid: str) -> None:
        """Create a new user."""
        session = db_session.get()
        if session is None:
            raise UnknownDatabaseError
        query = insert(User).values(hgramid=hgramid)
        await session.execute(query)
