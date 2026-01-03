import secrets
from urllib.parse import urlencode

from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse
from loguru import logger

from thatsoundapi.api.v1.models.spotify import StatusResponse, TokenRefreshResponse
from thatsoundapi.core.responses import SuccessResponse, create_success_response
from thatsoundapi.repositories.spotify_repository import SpotifyRepository
from thatsoundapi.services.spotify_service import SpotifyService
from thatsoundapi.settings import get_settings

spotify_router = APIRouter(tags=["Spotify"])


@spotify_router.get("")
async def spotify_login(hgramid: str) -> RedirectResponse:
    """Redirect user to Spotify login page."""
    logger.info("[{hgramid}] [spotify] login initiated", hgramid=hgramid[:8])

    settings = get_settings()
    state = secrets.token_hex(16)
    await SpotifyRepository.save_oauth_state(state, hgramid, ttl=settings.SPOTIFY_OAUTH_STATE_TTL)

    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": settings.SPOTIFY_SCOPES,
        "state": state,
    }

    return RedirectResponse(f"{settings.SPOTIFY_AUTHORIZE_URL}?{urlencode(params)}")


@spotify_router.post(
    "/refresh",
    response_model=SuccessResponse[TokenRefreshResponse],
    status_code=status.HTTP_200_OK,
)
async def refresh_spotify_tokens(htelegram_id: str) -> SuccessResponse[TokenRefreshResponse]:
    """Manually refresh Spotify tokens."""
    logger.info("[{htelegram_id}] [spotify] manual token refresh requested", htelegram_id=htelegram_id[:8])

    refreshed = await SpotifyService.refresh_token(htelegram_id)

    logger.success("[{htelegram_id}] [spotify] manual token refresh completed", htelegram_id=htelegram_id[:8])

    token_response = TokenRefreshResponse(
        htelegram_id=htelegram_id[:8],
        status="success",
        message="Tokens refreshed successfully",
        expires_in=refreshed["expires_in"],
    )
    return create_success_response(data=token_response)


@spotify_router.delete(
    "/tokens/",
    response_model=SuccessResponse[StatusResponse],
    status_code=status.HTTP_200_OK,
)
async def revoke_spotify_tokens(htelegram_id: str) -> SuccessResponse[StatusResponse]:
    """Revoke and delete Spotify tokens for a user."""
    logger.info("[{htelegram_id}] [spotify] revoking tokens", htelegram_id=htelegram_id[:8])

    await SpotifyRepository.delete_spotify_tokens(htelegram_id)

    logger.success("[{htelegram_id}] [spotify] tokens revoked", htelegram_id=htelegram_id[:8])

    status_response = StatusResponse(
        htelegram_id=htelegram_id[:8],
        status="success",
        message="Spotify tokens revoked successfully",
    )
    return create_success_response(data=status_response)
