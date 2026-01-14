import asyncio
import time

from loguru import logger

from thatsoundapi.api.v1.models.sounds import RecentTracksResponse, IntegrationsTracks, TrackView
from thatsoundapi.core.spotify.models import SpotifyTokens
from thatsoundapi.core.spotify.oauth import refresh_access_token
from thatsoundapi.core.spotify.service import get_recent_played_tracks as get_recent_played_tracks_spotify, get_current_playing_track as get_current_playing_track_spotify, play_order_sort as play_order_sort_spotify, build_tracks_object as build_tracks_object_spotify
from thatsoundapi.core.yandex.models import YandexToken
from thatsoundapi.core.yandex.service import get_recent_played_tracks as get_recent_played_tracks_yandex, get_current_playing_track as get_current_playing_track_yandex
from thatsoundapi.db.redis import RedisService
from thatsoundapi.settings import get_spotify_settings


async def prepare_spotify(redis: RedisService, hgramid: str, tokens: SpotifyTokens) -> list[TrackView]:
    spotify_settings = get_spotify_settings()

    now = int(time.time())
    time_until_expiry = tokens.expires_at - now if tokens.expires_at else 0

    if time_until_expiry <= spotify_settings.TOKEN_EXPIRE_LIMIT:
        tokens = await refresh_access_token(redis=redis, hgramid=hgramid, old_tokens=tokens)

    recent_tracks_task = get_recent_played_tracks_spotify(hgramid=hgramid, access_token=tokens.access_token)
    current_track_task = get_current_playing_track_spotify(hgramid=hgramid, access_token=tokens.access_token)

    recent_tracks_dict, current_track_dict = await asyncio.gather(
        recent_tracks_task,
        current_track_task,
    )

    raw_tracks = play_order_sort_spotify(raw_tracks=recent_tracks_dict.get("items", []))

    if current_track_dict:
        raw_tracks.insert(0, current_track_dict)
        raw_tracks.pop()

    try:
        tracks = build_tracks_object_spotify(raw_tracks=raw_tracks)
    except Exception as e:
        logger.error(
            "[{hgramid}] [sound] [spotify] failed to build tracks objects: {error_text}",
            hgramid=hgramid[:8],
            error_text=str(e)
        )
        return []

    return tracks


async def prepare_yandex(hgramid: str, token: YandexToken) -> list[TrackView]:
    recent_tracks_task = get_recent_played_tracks_yandex(hgramid=hgramid, access_token=token.access_token)
    current_track_task = get_current_playing_track_yandex(access_token=token.access_token)

    recent_tracks, current_track = await asyncio.gather(
        recent_tracks_task,
        current_track_task
    )


    if current_track:
        recent_tracks.insert(0, current_track)
        recent_tracks.pop()

    return recent_tracks


async def process_recent_played_tracks(redis: RedisService, hgramid: str) -> RecentTracksResponse:
    # Implement Last.FM and SoundCloud. Now only Spotify and Yandex.Music
    spotify_tokens, yandex_token = await asyncio.gather(
        redis.get_spotify_tokens(hgramid),
        redis.get_yandex_token(hgramid),
    )

    spotify_task = (
        prepare_spotify(redis=redis, hgramid=hgramid, tokens=spotify_tokens)
        if spotify_tokens
        else asyncio.sleep(0, result=[])
    )

    yandex_task = (
        prepare_yandex(hgramid=hgramid, token=yandex_token)
        if yandex_token
        else asyncio.sleep(0, result=[])
    )

    spotify_tracks, yandex_tracks = await asyncio.gather(
        spotify_task,
        yandex_task,
    )

    return RecentTracksResponse.model_construct(
        tracks=IntegrationsTracks.model_construct(
            spotify=spotify_tracks,
            yandex_music=yandex_tracks,
        )
    )
