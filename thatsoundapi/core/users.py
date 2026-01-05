from loguru import logger

from thatsoundapi.db.models import User
from thatsoundapi.repositories.user_repository import UserRepository


async def mention_user(hgramid: str) -> tuple[User, bool]:
    """Get or create user by hashed Telegram ID"""

    user = await UserRepository.get_by_hgramid(hgramid)

    if not user:
        user = await UserRepository.create(htelegram_id=hgramid)
        logger.info("[{hgramid}]: Created", hgramid=hgramid[:8])
        return user, True

    return user, False
