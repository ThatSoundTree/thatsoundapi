from fastapi import APIRouter, Depends, status
from loguru import logger

from thatsoundapi.api.v1.models.sounds import RecentTracksResponse
from thatsoundapi.api.v1.models.users import UserIntegrationsResponse
from thatsoundapi.core.integrations import user_integrations_service
from thatsoundapi.core.sounds import recent_played_tracks
from thatsoundapi.core.spotify.oauth import keep_token_alive as keep_token_alive_spotify
from thatsoundapi.db.connection import Transaction
from thatsoundapi.db.dependencies import get_transaction
from thatsoundapi.utils.auth import verify_basic_auth

user_router = APIRouter(tags=["Main"], dependencies=[Depends(verify_basic_auth)])


@user_router.get(
    "/{hgramid}/integrations",
    response_model=UserIntegrationsResponse,
    status_code=status.HTTP_200_OK,
)
async def user_integrations(
    hgramid: str,
    _: Transaction = Depends(get_transaction),
) -> UserIntegrationsResponse:
    """Get user integrations status."""

    response = await user_integrations_service(hgramid=hgramid)
    return response



@user_router.get(
    "/{hgramid}/recent",
    status_code=status.HTTP_200_OK,
    response_model=RecentTracksResponse,
)
@keep_token_alive_spotify
async def get_recent_tracks(
    hgramid: str,
    _: Transaction = Depends(get_transaction),
):
    """Get recently played tracks for a user (Spotify only)."""
    logger.info("[{hgramid}] recent tracks", hgramid=hgramid[:8])

    integrations = await user_integrations_service(hgramid=hgramid)
    tracks_response = await recent_played_tracks(hgramid=hgramid, integrations=integrations)
    logger.success(
        "[{hgramid}] [sound] fetch yandex_music={len_yandex} and spotify={len_spotify}",
        hgramid=hgramid[:8],
        len_yandex=len(tracks_response.tracks.yandex_music),
        len_spotify=len(tracks_response.tracks.spotify)
    )
    return tracks_response
