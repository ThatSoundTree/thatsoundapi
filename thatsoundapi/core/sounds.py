import asyncio
from loguru import logger

from thatsoundapi.api.v1.models.sounds import RecentTracksResponse, IntegrationsTracks
from thatsoundapi.api.v1.models.spotify import SpotifyTrack
from thatsoundapi.api.v1.models.users import UserIntegrationsResponse
from thatsoundapi.api.v1.models.yandex_music import YandexMusicTrack
from thatsoundapi.core.spotify.oauth import keep_token_alive
from thatsoundapi.core.spotify.service import get_recent_played_tracks as get_recent_played_tracks_spotify, get_current_playing_track as get_current_playing_track_spotify, play_order_sort as play_order_sort_spotify, build_tracks_object as build_tracks_object_spotify
from thatsoundapi.core.yandex.service import get_recent_played_tracks as get_recent_played_tracks_yandex, get_current_playing_track as get_current_playing_track_yandex


@keep_token_alive
async def prepare_spotify(hgramid: str) -> list[SpotifyTrack]:
    tracks_dict = await get_recent_played_tracks_spotify(hgramid=hgramid)
    current_track = await get_current_playing_track_spotify(hgramid=hgramid)
    raw_tracks = play_order_sort_spotify(raw_tracks=tracks_dict.get("items", []))

    if current_track:
        raw_tracks.insert(0, current_track)
        raw_tracks.pop()

    try:
        tracks = build_tracks_object_spotify(raw_tracks=raw_tracks)
    except Exception as e:
        logger.error("[{hgramid}] [sound] [spotify] failed to build tracks objects: {error_text}", hgramid=hgramid[:8],
                     error_text=str(e))
        return []

    return tracks


async def prepare_yandex(hgramid: str) -> list[YandexMusicTrack]:
    tracks = await get_recent_played_tracks_yandex(hgramid=hgramid)
    current_track = await get_current_playing_track_yandex(hgramid=hgramid)

    if current_track:
        tracks.insert(0, current_track)
        tracks.pop()

    return tracks


async def recent_played_tracks(hgramid: str, integrations: UserIntegrationsResponse) -> RecentTracksResponse:
    # Implement Last.FM. Now only Spotify and Yandex.Music
    spotify_tracks: list[SpotifyTrack] = []
    yandex_tracks: list[YandexMusicTrack] = []

    async with asyncio.TaskGroup() as tg:
        spotify_task = tg.create_task(prepare_spotify(hgramid=hgramid)) if integrations.spotify else None
        yandex_task = tg.create_task(prepare_yandex(hgramid=hgramid)) if integrations.YandexMusic else None

    if spotify_task:
        spotify_tracks = spotify_task.result()
    if yandex_task:
        yandex_tracks = yandex_task.result()

    result = IntegrationsTracks.model_construct(spotify=spotify_tracks, yandex_music=yandex_tracks)
    return RecentTracksResponse.model_construct(tracks=result)
