from loguru import logger

from thatsoundapi.api.v1.models.users import UserIntegrationsResponse
from thatsoundapi.db.redis import RedisClient
from thatsoundapi.repositories import UserRepository

async def user_integrations_service(hgramid: str) -> UserIntegrationsResponse:
    user_integrations = UserIntegrationsResponse()

    # Check if user exists
    user = await UserRepository.get_by_htelegram_id(hgramid)

    if not user:
        await UserRepository.create(hgramid=hgramid)
        logger.info("[{hgramid}]: Created", hgramid=hgramid[:8])
        return user_integrations

    spotify_integration = await RedisClient.has_spotify_integration(hgramid=hgramid)
    user_integrations.spotify = spotify_integration

    return user_integrations
