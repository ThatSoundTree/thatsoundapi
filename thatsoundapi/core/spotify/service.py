import datetime
import secrets
import time
from typing import Any
from urllib.parse import urlencode

from loguru import logger

from thatsoundapi.api.v1.models.spotify import SpotifyTrack
from thatsoundapi.utils.exceptions.spotify import NoSpotifyIntegrationError, UnknownSpotifyAPIError

from thatsoundapi.db.redis import RedisClient
from thatsoundapi.core.spotify.models import SpotifyTokens
from thatsoundapi.core.spotify.oauth import exchange_code_for_tokens, check_and_save_tokens, refresh_access_token
from thatsoundapi.settings import get_spotify_settings
from thatsoundapi.utils.http_client import HttpClient


async def initiate_login(hgramid: str) -> str:
    state = secrets.token_hex(16)
    spotify_settings = get_spotify_settings()
    redis = RedisClient.current()

    await redis.save_spotify_oauth_state(hgramid=hgramid, state=state, ttl=spotify_settings.OAUTH_STATE_TTL)

    params = {
        "client_id": spotify_settings.CLIENT_ID,
        "response_type": "code",
        "redirect_uri": spotify_settings.REDIRECT_URI,
        "scope": spotify_settings.SCOPES,
        "state": state,
    }

    return f"{spotify_settings.AUTHORIZE_URL}?{urlencode(params)}"


async def process_callback(hgramid: str, state: str, code: str):
    redis = RedisClient.current()
    await redis.delete_spotify_oauth_state(state=state)
    tokens = await exchange_code_for_tokens(hgramid=hgramid, code=code)
    await check_and_save_tokens(hgramid=hgramid, tokens=tokens)


async def process_refresh_tokens(hgramid: str):
    redis = RedisClient.current()
    tokens_dict = await redis.get_spotify_tokens(hgramid=hgramid)
    if not tokens_dict:
        logger.warning("[{hgramid}] [spotify] empty tokens", hgramid=hgramid[:8])
        raise NoSpotifyIntegrationError
    old_tokens = SpotifyTokens.model_validate(tokens_dict)
    await refresh_access_token(hgramid=hgramid, old_tokens=old_tokens)


async def get_recent_played_tracks(hgramid: str, limit: int = 15) -> dict[str, Any]:
    spotify_settings = get_spotify_settings()
    redis = RedisClient.current()
    tokens_dict = await redis.get_spotify_tokens(hgramid=hgramid)
    if not tokens_dict:
        raise NoSpotifyIntegrationError
    tokens = SpotifyTokens.model_validate(tokens_dict)

    response = await HttpClient.get(
        url=f"{spotify_settings.API_BASE_URL}/me/player/recently-played",
        headers = spotify_settings.get_api_call_header(access_token=tokens.access_token),
        params = {
            "limit": limit,
        }
    )

    if response.status_code != 200:
        logger.error("[{hgramid}] [spotify] unknown api error: {error_text}", hgramid=hgramid[:8], error_text=response.text[:200])
        raise UnknownSpotifyAPIError

    return response.json()  # type: ignore[no-any-return]


async def get_current_playing_track(hgramid: str) -> dict | None:
    spotify_settings = get_spotify_settings()
    redis = RedisClient.current()
    tokens_dict = await redis.get_spotify_tokens(hgramid=hgramid)
    if not tokens_dict:
        raise NoSpotifyIntegrationError
    tokens = SpotifyTokens.model_validate(tokens_dict)
    response = await HttpClient.get(
        url=f"{spotify_settings.API_BASE_URL}/me/player/currently-playing",
        headers=spotify_settings.get_api_call_header(access_token=tokens.access_token),
    )

    if response.status_code == 204:
        return None
    elif response.status_code != 200:
        logger.error("[{hgramid}] [spotify] unknown api error: {error_text}", hgramid=hgramid[:8], error_text=response.text[:200])
        return None

    data = response.json()
    is_playing = data.get("is_playing")
    playing_type = data.get("currently_playing_type")
    item = data.get("item")

    if not (is_playing and playing_type == "track" and item):
        return None

    timestamp_ms = data.get("timestamp", int(time.time() * 1000))
    played_at = datetime.datetime.fromtimestamp(timestamp_ms / 1000, tz=datetime.timezone.utc).isoformat()

    return {
        "track": item,
        "played_at": played_at
    }


def play_order_sort(raw_tracks: list) -> list:
    play_order = sorted(
        raw_tracks,
        key=lambda item: item.get("played_at", ""),
        reverse=True
    )

    unique_tracks = []
    seen_track_ids = set()

    for item in play_order:
        track = item.get("track", {})
        track_id = track.get("id")

        if not track_id or track_id in seen_track_ids:
            continue

        seen_track_ids.add(track_id)
        unique_tracks.append(item)

        if len(unique_tracks) >= 5:
            break

    return unique_tracks


def build_tracks_object(raw_tracks: list) -> list[SpotifyTrack]:
    spotify_tracks = []
    for item in raw_tracks:
        track_data = item["track"]
        artists = [artist["name"] for artist in track_data["artists"]]
        album_cover_url = extract_album_cover(album=track_data["album"])
        spotify_track = SpotifyTrack.model_construct(
            id=track_data["id"],
            name=track_data["name"],
            artists=artists,
            album_cover_url=album_cover_url,
            played_at=item["played_at"],
            url=item["track"].get("external_urls", {}).get("spotify")
        )
        spotify_tracks.append(spotify_track)

    return spotify_tracks

def extract_album_cover(album: dict[str, Any]) -> str | None:
    album_cover_url: str | None = None
    album_images = album.get("images", [])
    if album_images:
        medium_image = next((img for img in album_images if img.get("height") == 640), None)
        image = medium_image or album_images[0] or {}
        album_cover_url = image.get("url") if image else None

    return album_cover_url
