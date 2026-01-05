from fastapi import APIRouter, Query, status
from fastapi.responses import HTMLResponse
from loguru import logger

from thatsoundapi.core.spotify.service import process_callback as process_callback_spotify
from thatsoundapi.utils.exceptions.spotify import InvalidSpotifyOAuthStateError

from thatsoundapi.db.redis import RedisClient

callback_router = APIRouter()


@callback_router.get(
    "/spotify",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def spotify_callback(
    code: str = Query(..., description="Spotify authorization code"),
    state: str = Query(..., description="OAuth state parameter")
):
    """Callback from Spotify OAuth."""

    hgramid = await RedisClient.get_spotify_oauth_state(state=state)
    if not hgramid:
        logger.warning("[spotify] invalid or expired state: {state}", state[:8])
        raise InvalidSpotifyOAuthStateError

    logger.info("[{hgramid}] [spotify] callback", hgramid=hgramid[:8])
    await process_callback_spotify(hgramid=hgramid, state=state, code=code)

    return '<html><head><style>body { color: green; }</style></head><body><h1>Success! Return to <a href="https://t.me/thatsoundbot">@thatsoundbot</a></h1></body></html>'
