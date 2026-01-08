import inspect
import time
from functools import wraps
from typing import Callable, Any

from loguru import logger

from thatsoundapi.core.integrations import user_integrations_service
from thatsoundapi.utils.exceptions.spotify import SpotifyExchangeTokenError, SpotifyTokenError, \
    RefreshSpotifyTokenError, NoSpotifyIntegrationError

from thatsoundapi.db.redis import RedisClient
from thatsoundapi.core.spotify.models import SpotifyTokens
from thatsoundapi.settings import get_spotify_settings
from thatsoundapi.utils.http_client import HttpClient


async def exchange_code_for_tokens(hgramid: str, code: str) -> SpotifyTokens:
    spotify_settings = get_spotify_settings()

    response = await HttpClient.post(
        url=spotify_settings.TOKEN_URL,
        headers=spotify_settings.get_header(),
        data=spotify_settings.get_exchange_payload(code=code)
    )

    if response.status_code != 200:
        error_text = response.text[:200]
        logger.error("[{hgramid}] [spotify] tokens failed: {error_text}", hgramid=hgramid[:8], error_text=error_text)
        raise SpotifyExchangeTokenError

    logger.info("[{hgramid}] [spotify] exchanged code", hgramid=hgramid[:8])
    data = response.json()

    tokens = SpotifyTokens.model_construct(
        **data,
        expires_at=int(time.time()) + data["expires_in"]
    )
    return tokens



async def is_token_alive(hgramid: str, access_token: str) -> bool:
    spotify_settings = get_spotify_settings()
    response = await HttpClient.get(
        url=f"{spotify_settings.API_BASE_URL}/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if response.status_code != 200:
        logger.error("[{hgramid}] [spotify] failed check: {error_text}", hgramid=hgramid[:8], error_text=response.text)
        return False
    return True


async def check_and_save_tokens(hgramid: str, tokens: SpotifyTokens) -> None:
    is_alive = await is_token_alive(hgramid=hgramid, access_token=tokens.access_token)
    if not is_alive:
        raise SpotifyTokenError
    await RedisClient.save_spotify_tokens(hgramid=hgramid, tokens=tokens)
    logger.success("[{hgramid}] [spotify] saved tokens", hgramid=hgramid[:8])


async def refresh_access_token(hgramid: str, old_tokens: SpotifyTokens) -> None:
    spotify_settings = get_spotify_settings()

    response = await HttpClient.post(
        url=spotify_settings.TOKEN_URL,
        headers=spotify_settings.get_header(),
        data=spotify_settings.get_refresh_payload(refresh_token=old_tokens.refresh_token)
    )

    if response.status_code != 200:
        logger.error("[{hgramid}] [spotify] refresh failed: {error_text}", hgramid=hgramid[:8], error_text=response.text)
        raise RefreshSpotifyTokenError

    new_tokens_dict = response.json()
    new_tokens_dict['refresh_token'] = old_tokens.refresh_token

    if "refresh_token" in new_tokens_dict:
        logger.success("[{hgramid}] [spotify] updated refresh token!", hgramid=hgramid[:8])
        new_tokens_dict['refresh_token'] = new_tokens_dict.get("refresh_token")

    new_tokens = SpotifyTokens.model_construct(
        **new_tokens_dict,
        expires_at=int(time.time()) + new_tokens_dict["expires_in"]
    )

    await check_and_save_tokens(hgramid=hgramid, tokens=new_tokens)


def keep_token_alive(func: Callable) -> Callable:
    """Something in the way."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        spotify_settings = get_spotify_settings()
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        hgramid = bound_args.arguments.get('hgramid')

        if hgramid:

            integrations = await user_integrations_service(hgramid=hgramid)
            if not integrations.spotify:
                return await func(*args, **kwargs)

            tokens_dict = await RedisClient.get_spotify_tokens(hgramid=hgramid)
            if not tokens_dict:
                raise NoSpotifyIntegrationError
            tokens = SpotifyTokens.model_validate(tokens_dict)

            now = int(time.time())
            time_until_expiry = tokens.expires_at - now if tokens.expires_at else 0

            if time_until_expiry <= spotify_settings.TOKEN_EXPIRE_LIMIT:
                await refresh_access_token(hgramid=hgramid, old_tokens=tokens)
            #
            # is_alive = await is_token_alive(hgramid=hgramid, access_token=tokens.access_token)
            # if not is_alive:
            #     await refresh_access_token(hgramid=hgramid, tokens=tokens)
        return await func(*args, **kwargs)

    return wrapper
