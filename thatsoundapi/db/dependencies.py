from collections.abc import AsyncGenerator

from thatsoundapi.db.connection import Transaction
from thatsoundapi.db.redis import RedisClient, RedisService


async def get_transaction() -> AsyncGenerator[Transaction, None]:
    """Database transaction dependency. Commits on success, rolls back on exception."""
    transaction = Transaction()
    async with transaction:
        yield transaction


async def get_redis() -> RedisService:
    client = RedisClient.client()
    return RedisService(client)
