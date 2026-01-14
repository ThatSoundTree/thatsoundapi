import time
from urllib.parse import urlparse, parse_qs

from loguru import logger

from thatsoundapi.api.v1.models.sounds import TrackView
from thatsoundapi.core.yandex.current import get_current_track
from thatsoundapi.core.yandex.history import extract_tracks
from thatsoundapi.core.yandex.models import YandexToken
from thatsoundapi.core.yandex.oauth import check_and_save_token
from thatsoundapi.db.redis import RedisClient
from thatsoundapi.settings import get_yandex_settings
from thatsoundapi.utils.exceptions.yandex import UnknownYandexMusicAPIError
from thatsoundapi.utils.http_client import HttpClient


FULL_MODEL_MULTIPLIER = 2


def extract_token_data(
    hgramid: str,
    yandex_url: str,
) -> YandexToken:
    parsed = urlparse(yandex_url)
    params = parse_qs(parsed.fragment)

    expires_in = int(params["expires_in"][0])

    logger.info(
        "[{hgramid}] [yandex] token got",
        hgramid=hgramid[:8],
    )

    return YandexToken(
        access_token=params["access_token"][0],
        token_type=params["token_type"][0],
        expires_in=expires_in,
        expires_at=int(time.time()) + expires_in,
    )


async def process_callback(
    hgramid: str,
    query_url: str,
) -> None:
    redis = RedisClient.current()
    await redis.delete_yandex_token(hgramid=hgramid)

    token = extract_token_data(
        hgramid=hgramid,
        yandex_url=query_url,
    )

    await check_and_save_token(
        hgramid=hgramid,
        token=token,
    )


async def get_recent_played_tracks(
    hgramid: str,
    access_token: str,
    limit: int = 15
) -> list[TrackView]:
    settings = get_yandex_settings()

    response = await HttpClient.get(
        url=f"{settings.API_BASE_URL}/music-history",
        headers=settings.get_header(access_token=access_token),
        params={"fullModelsCount": limit * FULL_MODEL_MULTIPLIER},
    )

    if response.status_code != 200:
        logger.error(
            "[{hgramid}] [yandex] [recent] unknown api error: {error_text}",
            hgramid=hgramid[:8],
            error_text=response.text[:200]
        )
        raise UnknownYandexMusicAPIError

    items = [
        item
        for tab in response.json().get("result", {}).get("historyTabs", [])
        for item in tab.get("items", [])
    ]

    return extract_tracks(items, 5)


async def get_current_playing_track(
    access_token: str,
) -> TrackView | None:
    track = await get_current_track(access_token=access_token)
    return track
