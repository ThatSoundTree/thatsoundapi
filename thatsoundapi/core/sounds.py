from loguru import logger

from thatsoundapi.api.v1.models.spotify import SpotifyTrack
from thatsoundapi.core.spotify.service import get_recent_played_tracks as get_recent_played_tracks_spotify, get_current_playing_track as get_current_playing_track_spotify, play_order_sort as play_order_sort_spotify, build_tracks_object as build_tracks_object_spotify


async def recent_played_tracks(hgramid: str) -> list[SpotifyTrack]:
    # Implement yandex_music and Last.FM. Now only Spotify
    tracks_dict = await get_recent_played_tracks_spotify(hgramid=hgramid)
    current_track = await get_current_playing_track_spotify(hgramid=hgramid)
    raw_tracks = play_order_sort_spotify(raw_tracks=tracks_dict.get("items", []))

    if current_track:
        raw_tracks.insert(0, current_track)
        raw_tracks.pop()

    try:
        tracks = build_tracks_object_spotify(raw_tracks=raw_tracks)
    except Exception as e:
        logger.error("[{hgramid}] [sound] [spotify] failed to build tracks objects: {error_text}", hgramid=hgramid[:8], error_text=str(e))
        return []

    return tracks
