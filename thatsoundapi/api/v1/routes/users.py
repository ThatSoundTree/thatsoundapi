from fastapi import APIRouter, Depends, status
from loguru import logger

from thatsoundapi.api.v1.models.users import UserIntegrationsResponse
from thatsoundapi.db.connection import Transaction
from thatsoundapi.db.dependencies import get_transaction
from thatsoundapi.services.integrations_service import user_integrations_service
from thatsoundapi.services.spotify.oauth import keep_token_alive

user_router = APIRouter(tags=["Main"])


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
)
@keep_token_alive
async def get_recent_tracks(
    hgramid: str,
    _: Transaction = Depends(get_transaction),
):
    """Get recently played tracks for a user (Spotify only)."""
    logger.info("[{hgramid}] recent tracks", hgramid=hgramid[:8])

    await recent_tracks(hgramid=hgramid)

    tracks_data = await SpotifyService.get_recently_played_tracks(htelegram_id, limit=5)

    tracks = [SpotifyTrack(**track) for track in tracks_data]

    logger.success("[{htelegram_id}] [spotify] recent tracks retrieved", htelegram_id=htelegram_id[:8])

    response_data = RecentTracksResponse(
        tracks=tracks,
        count=len(tracks),
    )

    return create_success_response(data=response_data)
