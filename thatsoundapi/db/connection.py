"""Database connection management with context variables and transaction handling."""

from contextvars import ContextVar, Token

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from thatsoundapi.db.base import container

# Context variable for storing current database session
db_session: ContextVar[AsyncSession | None] = ContextVar("db_session", default=None)


class Transaction:
    """Async context manager for database transactions.

    Manages database session lifecycle with automatic commit/rollback
    and context variable management for dependency injection.

    Usage:
        async with Transaction():
            # Database operations here
            session = db_session.get()
            # Use session for queries
    """

    def __init__(self) -> None:
        """Initialize transaction context manager."""
        self.session: AsyncSession | None = None
        self.token: Token[AsyncSession | None] | None = None

    async def __aenter__(self) -> "Transaction":
        """Enter transaction context and create new session."""
        session_maker = container.resolve(async_sessionmaker)  # type: ignore[assignment]
        self.session = session_maker()
        self.token = db_session.set(self.session)
        return self

    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: object | None,
    ) -> None:
        """Exit transaction context with proper cleanup."""
        if self.session is None:
            return

        try:
            if exception:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()
            if self.token is not None:
                db_session.reset(self.token)
