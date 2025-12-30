from loguru import logger

from thatsoundapi.api.v1.models.users import Integrations
from thatsoundapi.db.models import User
from thatsoundapi.repositories.spotify_repository import SpotifyRepository
from thatsoundapi.repositories.user_repository import UserRepository


async def get_user_integrations(htelegram_id: str) -> Integrations:
    """Get user integrations status."""
    spotify_connected = await SpotifyRepository.has_valid_spotify_tokens(htelegram_id)
    return Integrations(spotify=spotify_connected)


async def mention_user(htelegram_id: str) -> tuple[User, bool, Integrations]:
    """Get or create user by hashed Telegram ID. Returns (user, is_new, integrations)."""
    user = await UserRepository.get_by_htelegram_id(htelegram_id)

    if not user:
        user = await UserRepository.create(htelegram_id=htelegram_id)
        logger.info("Created new user with htelegram_id: {htelegram_id}...", htelegram_id=htelegram_id[:8])
        integrations = await get_user_integrations(htelegram_id)
        return user, True, integrations

    logger.debug("Found existing user with htelegram_id: {htelegram_id}...", htelegram_id=htelegram_id[:8])
    integrations = await get_user_integrations(htelegram_id)
    return user, False, integrations
