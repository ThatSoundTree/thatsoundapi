from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse
from loguru import logger

from thatsoundapi.core.spotify.spotify_service import initiate_login, process_refresh_tokens

spotify_router = APIRouter(tags=["Spotify"])


@spotify_router.get("/login")
async def spotify_init_login(hgramid: str) -> RedirectResponse:
    """Redirect user to Spotify login page."""
    logger.info("[{hgramid}] [spotify] init", hgramid=hgramid[:8])
    redirect_url = await initiate_login(hgramid=hgramid)
    return RedirectResponse(url=redirect_url)


@spotify_router.get(
    "/refresh",
    status_code=status.HTTP_200_OK,
)
async def refresh_spotify_tokens(hgramid: str) -> None:
    """Manually refresh Spotify tokens."""
    logger.info("[{hgramid}] [spotify] refresh", hgramid=hgramid[:8])
    await process_refresh_tokens(hgramid=hgramid)

