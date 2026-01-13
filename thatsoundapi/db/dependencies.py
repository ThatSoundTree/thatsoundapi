from collections.abc import AsyncGenerator
from thatsoundapi.db.connection import Transaction
from thatsoundapi.db.redis import RedisClient


async def get_transaction() -> AsyncGenerator[Transaction, None]:
    """Database transaction dependency. Commits on success, rolls back on exception."""
    transaction = Transaction()
    async with transaction:
        yield transaction


async def get_redis() -> AsyncGenerator[RedisClient, None]:
    """Redis client dependency."""
    redis_client = RedisClient()
    async with redis_client:
        yield redis_client
