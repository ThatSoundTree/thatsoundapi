from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from loguru import logger

from thatsoundapi.api.v1.models.spotify import RecentTracksResponse, SpotifyTrack
from thatsoundapi.core.exceptions import BadRequestException
from thatsoundapi.core.responses import SuccessResponse, create_success_response
from thatsoundapi.db.connection import Transaction
from thatsoundapi.db.dependencies import get_transaction
from thatsoundapi.services.spotify_service import SpotifyService

sounds_router = APIRouter(tags=["Sounds"])


@sounds_router.get(
    "/recent-tracks/{htelegram_id}",
    response_model=SuccessResponse[RecentTracksResponse],
)
async def get_recent_tracks(
    htelegram_id: str,
    _: Transaction = Depends(get_transaction),
) -> SuccessResponse[RecentTracksResponse] | JSONResponse:
    """Get recently played tracks for a user (Spotify only)."""
    if not htelegram_id or not htelegram_id.strip():
        raise BadRequestException("htelegram_id cannot be empty")

    logger.info("[{htelegram_id}] [spotify] fetching recent tracks", htelegram_id=htelegram_id[:8])
    tracks_data = await SpotifyService.get_recently_played_tracks(htelegram_id, limit=5)

    tracks = [SpotifyTrack(**track) for track in tracks_data]

    logger.success("[{htelegram_id}] [spotify] recent tracks retrieved", htelegram_id=htelegram_id[:8])

    response_data = RecentTracksResponse(
        tracks=tracks,
        count=len(tracks),
    )

    response = create_success_response(data=response_data)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.model_dump(mode="json", exclude_none=True),
    )
