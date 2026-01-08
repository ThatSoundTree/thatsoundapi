from loguru import logger

from thatsoundapi.api.v1.models.users import UserIntegrationsResponse
from thatsoundapi.db.redis import RedisClient
from thatsoundapi.repositories import UserRepository

async def user_integrations_service(hgramid: str) -> UserIntegrationsResponse:
    user_integrations = UserIntegrationsResponse()
    user = await UserRepository.get_by_hgramid(hgramid)

    if not user:
        await UserRepository.create(hgramid=hgramid)
        logger.info("[{hgramid}]: Created", hgramid=hgramid[:8])
        return user_integrations

    spotify_integration = await RedisClient.has_spotify_integration(hgramid=hgramid)
    yandex_music_integrations = await RedisClient.has_yandex_music_integration(hgramid=hgramid)
    user_integrations.spotify = spotify_integration
    user_integrations.YandexMusic = yandex_music_integrations

    return user_integrations
