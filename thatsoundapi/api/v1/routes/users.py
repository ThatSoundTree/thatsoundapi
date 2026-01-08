from fastapi import APIRouter, Depends, status
from loguru import logger

from thatsoundapi.api.v1.models.users import UserIntegrationsResponse
from thatsoundapi.core.integrations import user_integrations_service
from thatsoundapi.core.yandex.service import current_playing_track
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
)
# @keep_token_alive
async def get_recent_tracks(
    hgramid: str,
    _: Transaction = Depends(get_transaction),
):
    """Get recently played tracks for a user (Spotify only)."""
    logger.info("[{hgramid}] recent tracks", hgramid=hgramid[:8])
    # result = await recent_played_tracks_yandex(hgramid=hgramid)
    # return result
    return await current_playing_track(hgramid=hgramid)
    # tracks = await recent_played_tracks_spotify(hgramid=hgramid)
    # logger.success("[{hgramid}] [sound] fetch len(tracks) == {len_tracks}", hgramid=hgramid[:8], len_tracks=len(tracks))
    # return RecentTracksResponse(tracks=tracks)
