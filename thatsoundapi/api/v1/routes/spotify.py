from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse
from loguru import logger
from thatsoundapi.core.spotify.service import initiate_login, process_refresh_tokens
from thatsoundapi.db import get_redis
from thatsoundapi.db.redis import RedisClient
from thatsoundapi.utils.auth import verify_basic_auth


spotify_router = APIRouter(tags=["Spotify"])


@spotify_router.get("/login")
async def spotify_init_login(hgramid: str, __: RedisClient = Depends(get_redis)) -> RedirectResponse:
    """Redirect user to Spotify login page."""
    logger.info("[{hgramid}] [spotify] init", hgramid=hgramid[:8])
    redirect_url = await initiate_login(hgramid=hgramid)
    return RedirectResponse(url=redirect_url)


@spotify_router.get(
    "/refresh",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_basic_auth)],
)
async def refresh_spotify_tokens(hgramid: str, __: RedisClient = Depends(get_redis)) -> None:
    """Manually refresh Spotify tokens."""
    logger.info("[{hgramid}] [spotify] refresh", hgramid=hgramid[:8])
    await process_refresh_tokens(hgramid=hgramid)
