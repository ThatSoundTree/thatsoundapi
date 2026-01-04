from loguru import logger

from thatsoundapi.core.exceptions import SpotifyExchangeTokenError, SpotifyTokenError
from thatsoundapi.db.redis import RedisClient
from thatsoundapi.services.spotify.models import SpotifyTokens
from thatsoundapi.settings import get_spotify_settings
from thatsoundapi.utils.http_client import HttpClient


async def exchange_code_for_tokens(hgramid: str, code: str) -> SpotifyTokens:
    spotify_settings = get_spotify_settings()

    response = await HttpClient.post(
        url=spotify_settings.TOKEN_URL,
        headers=spotify_settings.get_header(),
        data=spotify_settings.get_payload(code=code)
    )

    if response.status_code != 200:
        error_text = response.text[:200]
        logger.error("[{hgramid}] [spotify] tokens failed: {error_text}", hgramid=hgramid[:8], error_text=error_text)
        raise SpotifyExchangeTokenError

    logger.info("[{hgramid}] [spotify] exchanged code", hgramid=hgramid[:8])
    return SpotifyTokens.model_validate(response.json())



async def check_token(hgramid: str, access_token: str) -> None:
    spotify_settings = get_spotify_settings()
    response = await HttpClient.get(
        url=f"{spotify_settings.API_BASE_URL}/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if response.status_code != 200:
        logger.error("[{hgramid}] [spotify] failed check: {error_text}", hgramid=hgramid[:8], error_text=response.text)
        raise SpotifyTokenError


async def check_and_save_tokens(hgramid: str, tokens: SpotifyTokens) -> None:
    await check_token(hgramid=hgramid, access_token=tokens.access_token)
    await RedisClient.save_spotify_tokens(hgramid=hgramid[:8], tokens=tokens)
    logger.success("[{hgramid}] [spotify] saved tokens", hgramid=hgramid[:8])
