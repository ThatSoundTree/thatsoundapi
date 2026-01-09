import time
from urllib.parse import urlparse, parse_qs

from loguru import logger

from thatsoundapi.api.v1.models.yandex_music import YandexMusicTrack
from thatsoundapi.core.yandex.current import get_current_track
from thatsoundapi.core.yandex.history import extract_tracks
from thatsoundapi.core.yandex.models import YandexToken
from thatsoundapi.core.yandex.oauth import check_and_save_token
from thatsoundapi.db.redis import RedisClient
from thatsoundapi.settings import get_yandex_settings
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
    await RedisClient.delete_yandex_token(hgramid=hgramid)

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
    limit: int = 15,
) -> list[YandexMusicTrack]:
    settings = get_yandex_settings()

    token = YandexToken.model_validate(
        await RedisClient.get_yandex_token(hgramid=hgramid)
    )

    response = await HttpClient.get(
        url=f"{settings.API_BASE_URL}/music-history",
        headers=settings.get_header(access_token=token.access_token),
        params={"fullModelsCount": limit * FULL_MODEL_MULTIPLIER},
    )

    items = [
        item
        for tab in response.json().get("result", {}).get("historyTabs", [])
        for item in tab.get("items", [])
    ]

    return extract_tracks(items, 5)


async def get_current_playing_track(
    hgramid: str,
) -> YandexMusicTrack | None:
    token = YandexToken.model_validate(
        await RedisClient.get_yandex_token(hgramid=hgramid)
    )

    track = await get_current_track(token.access_token)
    return track
