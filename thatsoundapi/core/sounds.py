from loguru import logger

from thatsoundapi.api.v1.models.sounds import RecentTracksResponse, IntegrationsTracks
from thatsoundapi.api.v1.models.spotify import SpotifyTrack
from thatsoundapi.api.v1.models.users import UserIntegrationsResponse
from thatsoundapi.api.v1.models.yandex_music import YandexMusicTrack
from thatsoundapi.core.spotify.service import get_recent_played_tracks as get_recent_played_tracks_spotify, get_current_playing_track as get_current_playing_track_spotify, play_order_sort as play_order_sort_spotify, build_tracks_object as build_tracks_object_spotify
from thatsoundapi.core.yandex.service import get_recent_played_tracks as get_recent_played_tracks_yandex, get_current_playing_track as get_current_playing_track_yandex

async def prepare_spotify(hgramid: str) -> list[SpotifyTrack]:
    tracks_dict = await get_recent_played_tracks_spotify(hgramid=hgramid)
    current_track = await get_current_playing_track_spotify(hgramid=hgramid)
    raw_tracks = play_order_sort_spotify(raw_tracks=tracks_dict.get("items", []))

    if current_track:
        current_track_id = current_track.get("track", {}).get("id")
        raw_tracks = [t for t in raw_tracks if t.get("track", {}).get("id") != current_track_id]
        raw_tracks.insert(0, current_track)
        if raw_tracks:
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
        tracks = [t for t in tracks if t.id != current_track.id]
        tracks.insert(0, current_track)
        if tracks:
            tracks.pop()

    return tracks


async def recent_played_tracks(hgramid: str, integrations: UserIntegrationsResponse) -> RecentTracksResponse:
    # Implement Last.FM. Now only Spotify and Yandex.Music
    spotify_tracks, yandex_tracks = [], []
    if integrations.spotify:
        spotify_tracks = await prepare_spotify(hgramid=hgramid)
    if integrations.YandexMusic:
        yandex_tracks = await prepare_yandex(hgramid=hgramid)

    result = IntegrationsTracks.model_construct(spotify=spotify_tracks,yandex_music=yandex_tracks)
    return RecentTracksResponse.model_construct(tracks=result)
