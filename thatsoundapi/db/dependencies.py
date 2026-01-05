from collections.abc import AsyncGenerator
from thatsoundapi.db.connection import Transaction


async def get_transaction() -> AsyncGenerator[Transaction, None]:
    """Database transaction dependency. Commits on success, rolls back on exception."""
    transaction = Transaction()
    async with transaction:
        yield transaction
