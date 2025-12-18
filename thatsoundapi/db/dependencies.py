"""FastAPI dependencies for database session management."""

from sqlalchemy.ext.asyncio import AsyncSession

from thatsoundapi.db.connection import db_session


async def get_db_session() -> AsyncSession:
    """FastAPI dependency to get current database session from context.

    Raises:
        RuntimeError: If no database session is available in context.

    Returns:
        AsyncSession: Current database session.
    """
    session = db_session.get()
    if session is None:
        raise RuntimeError(
            "Database session not found in context. "
            "Ensure Transaction context manager is used."
        )
    return session
