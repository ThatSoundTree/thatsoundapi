from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from thatsoundapi.core.exceptions import DatabaseError
from thatsoundapi.db.connection import Transaction, db_session


async def get_db_session() -> AsyncSession:
    """Get current database session from context."""
    session = db_session.get()
    if session is None:
        raise DatabaseError(
            "Database session not found in context. "
            "Ensure Transaction dependency is used."
        )
    return session


async def get_transaction() -> AsyncGenerator[Transaction, None]:
    """Database transaction dependency. Commits on success, rolls back on exception."""
    async with Transaction() as transaction:
        yield transaction


async def get_optional_transaction() -> AsyncGenerator[Transaction | None, None]:
    """Optional database transaction dependency."""
    async with Transaction() as transaction:
        yield transaction
