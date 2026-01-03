import base64
import time
from typing import List

import httpx
from fastapi import status
from loguru import logger

from thatsoundapi.core.exceptions import UnauthorizedError, NotFoundError, BadRequestError
from thatsoundapi.repositories.spotify_repository import SpotifyRepository
from thatsoundapi.settings import get_settings


class SpotifyService:
    """Service for interacting with Spotify Web API"""

    @staticmethod
    def _get_auth_header() -> str:
        settings = get_settings()
        credentials = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET.get_secret_value()}"
        return base64.b64encode(credentials.encode()).decode()

    @staticmethod
    async def exchange_code_for_tokens(code: str, redirect_uri: str) -> dict:
        settings = get_settings()
        auth_header = SpotifyService._get_auth_header()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.SPOTIFY_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
                headers={
                    "Authorization": f"Basic {auth_header}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )

        if response.status_code != 200:
            error_text = response.text[:200]
            logger.error(
                "Failed to exchange code for tokens",
                status_code=response.status_code,
                error=error_text,
            )
            raise BadRequestError(
                status.HTTP_400_BAD_REQUEST, "Failed to exchange code for tokens"
            )

        result: dict[str, str | int] = response.json()
        return result

    @staticmethod
    async def handle_oauth_callback(code: str, redirect_uri: str, htelegram_id: str) -> None:
        tokens = await SpotifyService.exchange_code_for_tokens(code, redirect_uri)

        await SpotifyRepository.save_spotify_tokens(
            htelegram_id=htelegram_id,
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            expires_in=tokens["expires_in"],
            token_type=tokens.get("token_type", "Bearer"),
        )

    @staticmethod
    async def get_valid_access_token(htelegram_id: str) -> str:
        tokens = await SpotifyRepository.get_spotify_tokens(htelegram_id)
        if not tokens:
            logger.warning("Spotify tokens not found", htelegram_id=htelegram_id[:8])
            raise UnauthorizedError(
                status.HTTP_401_UNAUTHORIZED, "Spotify not connected. Please authenticate first."
            )

        current_time = int(time.time())
        expires_at = tokens.get("expires_at", 0)
        expires_at_int = int(expires_at) if isinstance(expires_at, (str, int)) else 0
        if expires_at_int <= current_time:
            logger.info("Access token expired, refreshing", htelegram_id=htelegram_id[:8])
            await SpotifyService._refresh_access_token(htelegram_id, tokens)
            tokens = await SpotifyRepository.get_spotify_tokens(htelegram_id)
            if not tokens:
                logger.error("Failed to get tokens after refresh", htelegram_id=htelegram_id[:8])
                raise UnauthorizedError(
                    status.HTTP_401_UNAUTHORIZED, "Failed to refresh Spotify token"
                )
            logger.success("Access token refreshed", htelegram_id=htelegram_id[:8])

        access_token_value = tokens.get("access_token")
        if not access_token_value or not isinstance(access_token_value, str):
            raise UnauthorizedError(status.HTTP_401_UNAUTHORIZED, "Invalid access token format")
        return str(access_token_value)

    @staticmethod
    async def _refresh_access_token(htelegram_id: str, tokens: dict) -> None:
        refresh_token = tokens.get("refresh_token")
        if not refresh_token:
            logger.error("Refresh token not available", htelegram_id=htelegram_id[:8])
            raise UnauthorizedError(
                status.HTTP_401_UNAUTHORIZED, "Refresh token not available"
            )

        settings = get_settings()
        auth_header = SpotifyService._get_auth_header()

        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                settings.SPOTIFY_TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                headers={
                    "Authorization": f"Basic {auth_header}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )

        if token_response.status_code != 200:
            logger.error(
                "Failed to refresh Spotify token",
                htelegram_id=htelegram_id[:8],
                status_code=token_response.status_code,
                response=token_response.text[:200],
            )
            raise UnauthorizedError(
                status.HTTP_401_UNAUTHORIZED, "Failed to refresh Spotify token"
            )

        new_tokens = token_response.json()

        await SpotifyRepository.update_spotify_access_token(
            htelegram_id=htelegram_id,
            access_token=new_tokens["access_token"],
            expires_in=new_tokens["expires_in"],
        )

        if "refresh_token" in new_tokens:
            logger.info("New refresh token received", htelegram_id=htelegram_id[:8])
            await SpotifyRepository.save_spotify_tokens(
                htelegram_id=htelegram_id,
                access_token=new_tokens["access_token"],
                refresh_token=new_tokens["refresh_token"],
                expires_in=new_tokens["expires_in"],
                token_type=new_tokens.get("token_type", "Bearer"),
            )

    @staticmethod
    async def refresh_token(htelegram_id: str) -> dict:
        tokens = await SpotifyRepository.get_spotify_tokens(htelegram_id)
        if not tokens:
            logger.warning("Spotify tokens not found for refresh", htelegram_id=htelegram_id[:8])
            raise UnauthorizedError(
                status.HTTP_401_UNAUTHORIZED, "Spotify not connected. Please authenticate first."
            )

        await SpotifyService._refresh_access_token(htelegram_id, tokens)

        new_tokens = await SpotifyRepository.get_spotify_tokens(htelegram_id)
        if not new_tokens:
            raise UnauthorizedError(
                status.HTTP_401_UNAUTHORIZED, "Failed to refresh Spotify token"
            )

        access_token = new_tokens.get("access_token")
        expires_in = new_tokens.get("expires_in")

        if not access_token:
            logger.error("Access token missing after refresh", htelegram_id=htelegram_id[:8])
            raise UnauthorizedError(status.HTTP_401_UNAUTHORIZED, "Access token missing after refresh")

        if expires_in is None:
            logger.error("Expires_in missing after refresh", htelegram_id=htelegram_id[:8])
            raise UnauthorizedError(status.HTTP_401_UNAUTHORIZED, "Expires_in missing after refresh")

        return {
            "access_token": str(access_token),
            "expires_in": int(expires_in),
            "token_type": new_tokens.get("token_type", "Bearer"),
        }

    @staticmethod
    async def get_recently_played_tracks(htelegram_id: str, limit: int = 5) -> List[dict]:
        settings = get_settings()
        access_token = await SpotifyService.get_valid_access_token(htelegram_id)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SPOTIFY_API_BASE_URL}/me/player/recently-played",
                params={"limit": min(limit, 50)},
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
            )

        if response.status_code == 401:
            logger.warning("Spotify API returned 401, attempting token refresh", htelegram_id=htelegram_id[:8])
            tokens = await SpotifyRepository.get_spotify_tokens(htelegram_id)
            if tokens:
                await SpotifyService._refresh_access_token(htelegram_id, tokens)
                access_token = await SpotifyService.get_valid_access_token(htelegram_id)

                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{settings.SPOTIFY_API_BASE_URL}/me/player/recently-played",
                        params={"limit": min(limit, 50)},
                        headers={
                            "Authorization": f"Bearer {access_token}",
                        },
                    )

        if response.status_code != 200:
            error_detail = response.text[:200]
            if response.status_code == 204:
                logger.info("No recently played tracks found", htelegram_id=htelegram_id[:8])
                raise NotFoundError()
            logger.error(
                "Spotify API error",
                htelegram_id=htelegram_id[:8],
                status_code=response.status_code,
                error=error_detail,
            )
            raise UnauthorizedError(
                status.HTTP_401_UNAUTHORIZED, "Failed to retrieve recently played tracks from Spotify"
            )

        data = response.json()
        items = data.get("items", [])

        logger.info("Retrieved recently played tracks", htelegram_id=htelegram_id[:8], count=len(items[:limit]))

        tracks = []
        for item in items[:limit]:
            track = item.get("track", {})
            artists = [artist.get("name") for artist in track.get("artists", [])]
            album = track.get("album", {})

            # Get album cover URL (prefer medium size, fallback to first available)
            album_cover_url = None
            album_images = album.get("images", [])
            if album_images:
                # Prefer medium size (640x640), fallback to largest (first) or smallest (last)
                medium_image = next((img for img in album_images if img.get("height") == 640), None)
                album_cover_url = (medium_image or album_images[0] or {}).get("url")

            tracks.append({
                "id": track.get("id"),
                "name": track.get("name"),
                "artists": artists,
                "album": album.get("name"),
                "album_cover_url": album_cover_url,
                "external_urls": track.get("external_urls", {}).get("spotify"),
                "played_at": item.get("played_at"),
                "duration_ms": track.get("duration_ms"),
                "preview_url": track.get("preview_url"),
            })

        return tracks
