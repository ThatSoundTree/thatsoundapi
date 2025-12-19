from loguru import logger

from thatsoundapi.db.models import User
from thatsoundapi.repositories.user_repository import UserRepository


async def mention_user(htelegram_id: str) -> tuple[User, bool]:
    """Get or create user by hashed Telegram ID. Returns (user, is_new)."""
    user = await UserRepository.get_by_htelegram_id(htelegram_id)

    if not user:
        user = await UserRepository.create(htelegram_id=htelegram_id)
        logger.info(f"Created new user with htelegram_id: {htelegram_id[:8]}...")
        return user, True

    logger.debug(f"Found existing user with htelegram_id: {htelegram_id[:8]}...")
    return user, False
