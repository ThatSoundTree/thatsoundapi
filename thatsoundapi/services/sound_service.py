from loguru import logger

from thatsoundapi.api.v1.models.spotify import SpotifyTrack
from thatsoundapi.services.spotify.spotify_service import get_recent_played_tracks, get_current_playing_track, \
    build_tracks_object, play_order_sort


async def recent_played_tracks(hgramid: str) -> list[SpotifyTrack]:
    # Implement yandex_music and Last.FM. Now only Spotify
    tracks_dict = await get_recent_played_tracks(hgramid=hgramid)
    current_track = await get_current_playing_track(hgramid=hgramid)
    raw_tracks = play_order_sort(raw_tracks=tracks_dict.get("items", []))

    if current_track:
        raw_tracks.insert(0, current_track)

    try:
        tracks = build_tracks_object(raw_tracks=raw_tracks)
    except Exception as e:
        logger.error("[{hgramid}] [sound] [spotify] failed to build tracks objects: {error_text}", hgramid=hgramid[:8], error_text=str(e))
        return []

    return tracks
