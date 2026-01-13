from fastapi import APIRouter, Depends, status, Query
from loguru import logger
from fastapi.responses import JSONResponse

from thatsoundapi.api.v1.models.sounds import RecentTracksResponse, Scrobble
from thatsoundapi.api.v1.models.users import UserIntegrationsResponse
from thatsoundapi.core.integrations import user_integrations_service
from thatsoundapi.core.scrobbles import process_scrobble_track, save_cached_url
from thatsoundapi.core.sounds import recent_played_tracks
from thatsoundapi.db.connection import Transaction
from thatsoundapi.db.dependencies import get_transaction, get_redis
from thatsoundapi.db.redis import RedisClient
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
    __: RedisClient = Depends(get_redis),
) -> UserIntegrationsResponse:
    """Get user integrations status."""

    response = await user_integrations_service(hgramid=hgramid)
    return response



@user_router.get(
    "/{hgramid}/recent",
    status_code=status.HTTP_200_OK,
    response_model=RecentTracksResponse,
)
async def get_recent_tracks(
    hgramid: str,
    _: Transaction = Depends(get_transaction),
    __: RedisClient = Depends(get_redis)
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


@user_router.get(
    "/{hgramid}/scrobble",
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE
)
async def scrobble_track(
    hgramid: str,
    track_id: str = Query(..., description="Track ID"),
    track_provider: int = Query(..., description="Track provider ID (i.e spotify=1)"),
    _: Transaction = Depends(get_transaction),
):
    logger.info(
        "[{hgramid}] scrobbling {track_id} from {provider_id}",
        hgramid=hgramid[:8],
        track_id=track_id[:8],
        provider_id=track_provider
    )

    scrobble = await process_scrobble_track(hgramid=hgramid, provider_id=track_provider, external_track_id=track_id)
    if isinstance(scrobble, str):
        return JSONResponse(
            content={"tfile_url": scrobble},
            status_code=status.HTTP_200_OK,
        )

    return Scrobble.model_validate(scrobble)


@user_router.patch(
    "/{hgramid}/scrobble/",
    status_code=status.HTTP_200_OK
)
async def save_tfile_url(
    hgramid: str,
    external_track_id: str = Query(..., description="External track ID"),
    tfile_url: str = Query(..., description="Telegram file url for re-using"),
    _: Transaction = Depends(get_transaction)
):
    logger.info(
        "[{hgramid}] saving track {external_track_id} from {tfile_url}",
        hgramid=hgramid[:8],
        external_track_id=external_track_id,
        tfile_url=tfile_url[8:],
    )

    await save_cached_url(tfile_url=tfile_url, external_track_id=external_track_id)
