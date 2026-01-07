import time
from typing import Optional
from urllib.parse import urlparse, parse_qs

from thatsoundapi.api.v1.models.yandex_music import YandexMusicTrack
from thatsoundapi.core.yandex.helpers import extract_track_id, extract_full_model, get_track_played_at
from thatsoundapi.core.yandex.mapping import create_track_model
from thatsoundapi.core.yandex.models import YandexToken
from thatsoundapi.core.yandex.oauth import check_and_save_token
from thatsoundapi.db.redis import RedisClient
from thatsoundapi.settings import get_yandex_settings
from thatsoundapi.utils.http_client import HttpClient


DEFAULT_TRACK_LIMIT = 15
DEFAULT_FULL_MODELS_COUNT = 25


def get_track_by_id(
    access_token: str,
    track_id: str
) -> Optional[YandexMusicTrack]:
    yandex_settings = get_yandex_settings()
    response = HttpClient.get(
        url=f"{yandex_settings.API_BASE_URL}/tracks",
        headers={"Authorization": f"OAuth {access_token}"},
        params={"track-ids": track_id},
    )

    if response.status_code != 200:
        return None

    result = response.json().get("result")
    if not result:
        return None

    track = result[0]

    return create_track_model(
        {
            "id": track.get("id"),
            "title": track.get("title"),
            "artists": track.get("artists"),
            "albums": track.get("albums"),
        }
    )

def process_track_item(
    item: dict,
    played_at: Optional[str],
    access_token: Optional[str] = None,
) -> Optional[YandexMusicTrack]:

    if item.get("type") != "track":
        return None

    full_model = extract_full_model(item)
    if not full_model:
        return None


    if not full_model.get("albums") and access_token:
        track_id = extract_track_id(item)
        if track_id:
            track = get_track_by_id(access_token, track_id)
            if track:
                track.played_at = played_at
                return track

    return create_track_model(full_model, played_at)


def process_history_items(
    items: list[dict],
    limit: int,
    access_token: Optional[str] = None,
) -> list[YandexMusicTrack]:

    tracks: list[YandexMusicTrack] = []

    for item in items:
        played_at = get_track_played_at(item)

        for track_item in item.get("tracks", []):
            track = process_track_item(track_item, played_at, access_token)
            if not track:
                continue

            tracks.append(track)
            if len(tracks) >= limit:
                return tracks

    return tracks


async def get_recent_played_tracks(
    hgramid: str,
    limit: int = DEFAULT_TRACK_LIMIT,
    full_models_count: int = DEFAULT_FULL_MODELS_COUNT,
) -> list[YandexMusicTrack]:
    yandex_settings = get_yandex_settings()
    token_data = await RedisClient.get_yandex_token(hgramid=hgramid)
    token = YandexToken.model_validate(token_data)

    response = await HttpClient.get(
        url=f"{yandex_settings.API_BASE_URL}/music-history",
        headers={"Authorization": f"OAuth {token.access_token}"},
        params={"fullModelsCount": max(full_models_count, limit * 2)},
    )

    result = response.json().get("result") or {}
    history_tabs = result.get("historyTabs") or []

    items = [
        item
        for tab in history_tabs
        for item in tab.get("items", [])
    ]

    return process_history_items(items, limit, token.access_token)




def extract_token_data(hgramid: str, yandex_url: str) -> YandexToken:
    parsed_url = urlparse(yandex_url)
    fragment = parsed_url.fragment
    raw_params = parse_qs(fragment, strict_parsing=True)

    params = {
        key: values[0] if values else ""
        for key, values in raw_params.items()
    }

    expires_in = int(params["expires_in"])

    logger.info("[{hgramid}] [yandex] token got", hgramid=hgramid[:8])

    return YandexToken(
        access_token=params["access_token"],
        token_type=params["token_type"],
        expires_in=expires_in,
        expires_at=int(time.time()) + expires_in,
    )



async def process_callback(hgramid: str, query_url: str):
    await RedisClient.delete_yandex_token(hgramid=hgramid)
    yandex_token = extract_token_data(hgramid=hgramid, yandex_url=query_url)
    await check_and_save_token(hgramid=hgramid, token=yandex_token)
