import secrets
from urllib.parse import urlencode

from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse, RedirectResponse
from loguru import logger

from thatsoundapi.api.v1.models.spotify import StatusResponse, TokenRefreshResponse
from thatsoundapi.core.exceptions import BadRequestException
from thatsoundapi.core.responses import SuccessResponse, create_success_response
from thatsoundapi.repositories.spotify_repository import SpotifyRepository
from thatsoundapi.services.spotify_service import SpotifyService
from thatsoundapi.settings import get_settings

spotify_router = APIRouter(tags=["Spotify"])


@spotify_router.get("/login/{htelegram_id}")
async def spotify_login(htelegram_id: str) -> RedirectResponse:
    """Redirect user to Spotify login page."""
    logger.info("[{htelegram_id}] [spotify] login initiated", htelegram_id=htelegram_id[:8])

    settings = get_settings()
    state = secrets.token_hex(16)
    await SpotifyRepository.save_oauth_state(state, htelegram_id, ttl=settings.SPOTIFY_OAUTH_STATE_TTL)

    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": settings.SPOTIFY_SCOPES,
        "state": state,
    }

    return RedirectResponse(f"{settings.SPOTIFY_AUTHORIZE_URL}?{urlencode(params)}")


@spotify_router.get(
    "/callback",
    response_model=SuccessResponse[StatusResponse],
)
async def spotify_callback(
    code: str = Query(..., description="Spotify authorization code"),
    state: str = Query(..., description="OAuth state parameter")
) -> SuccessResponse[StatusResponse] | JSONResponse:
    """Callback from Spotify OAuth."""
    htelegram_id = await SpotifyRepository.get_oauth_state(state)
    if not htelegram_id:
        logger.warning("[spotify] invalid or expired OAuth state: {state}", state=state[:8])
        raise BadRequestException(detail="Invalid or expired state")

    logger.info("[{htelegram_id}] [spotify] OAuth callback processing", htelegram_id=htelegram_id[:8])
    await SpotifyRepository.delete_oauth_state(state)

    settings = get_settings()
    await SpotifyService.handle_oauth_callback(code, settings.SPOTIFY_REDIRECT_URI, htelegram_id)

    logger.success("[{htelegram_id}] [spotify] OAuth completed successfully", htelegram_id=htelegram_id[:8])
    status_response = StatusResponse(
        htelegram_id=htelegram_id[:8],
        status="success",
        message="Spotify tokens saved successfully",
    )
    response_data = create_success_response(data=status_response)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_data.model_dump(mode="json", exclude_none=True),
    )


@spotify_router.post(
    "/refresh/{htelegram_id}",
    response_model=SuccessResponse[TokenRefreshResponse],
)
async def refresh_spotify_tokens(htelegram_id: str) -> SuccessResponse[TokenRefreshResponse] | JSONResponse:
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
    response_data = create_success_response(data=token_response)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_data.model_dump(mode="json", exclude_none=True),
    )


@spotify_router.delete(
    "/tokens/{htelegram_id}",
    response_model=SuccessResponse[StatusResponse],
)
async def revoke_spotify_tokens(htelegram_id: str) -> SuccessResponse[StatusResponse] | JSONResponse:
    """Revoke and delete Spotify tokens for a user."""
    logger.info("[{htelegram_id}] [spotify] revoking tokens", htelegram_id=htelegram_id[:8])

    await SpotifyRepository.delete_spotify_tokens(htelegram_id)

    logger.success("[{htelegram_id}] [spotify] tokens revoked", htelegram_id=htelegram_id[:8])

    status_response = StatusResponse(
        htelegram_id=htelegram_id[:8],
        status="success",
        message="Spotify tokens revoked successfully",
    )
    response_data = create_success_response(data=status_response)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_data.model_dump(mode="json", exclude_none=True),
    )
