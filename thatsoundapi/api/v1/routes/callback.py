from fastapi import APIRouter, Query, status, Depends
from fastapi.responses import HTMLResponse
from loguru import logger

from thatsoundapi.core.spotify.service import process_callback as process_callback_spotify
from thatsoundapi.core.yandex.service import process_callback as process_callback_yandex
from thatsoundapi.db import Transaction, get_transaction, get_redis
from thatsoundapi.repositories import UserRepository
from thatsoundapi.utils.exceptions.app import UserNotFoundError
from thatsoundapi.utils.exceptions.spotify import InvalidSpotifyOAuthStateError

from thatsoundapi.db.redis import RedisService

callback_router = APIRouter()


@callback_router.get(
    "/spotify",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def spotify_callback(
    code: str = Query(..., description="Spotify authorization code"),
    state: str = Query(..., description="OAuth state parameter"),
    redis: RedisService = Depends(get_redis)
):
    """Callback from Spotify OAuth."""

    hgramid = await redis.get_spotify_oauth_state(state=state)
    if not hgramid:
        logger.warning("[spotify] invalid or expired state: {state}", state[:8])
        raise InvalidSpotifyOAuthStateError

    logger.info("[{hgramid}] [spotify] callback", hgramid=hgramid[:8])
    await process_callback_spotify(redis=redis, hgramid=hgramid, state=state, code=code)

    return '<html><head><style>body { color: green; }</style></head><body><h1>Success! Return to <a href="https://t.me/thatsoundbot">@thatsoundbot</a></h1></body></html>'


@callback_router.get(
    "/yandex",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def yandex_callback(
    hgramid: str = Query(..., description="Hashed telegram id"),
    url: str = Query(..., description="Authorized yandex url"),
    redis: RedisService = Depends(get_redis),
    _: Transaction = Depends(get_transaction)
):

    user = await UserRepository.get_by_hgramid(hgramid=hgramid)
    if not user:
        logger.warning("[yandex] invalid hgramid=",hgramid=hgramid[:8])
        raise UserNotFoundError

    logger.info("[{hgramid}] [yandex] callback", hgramid=hgramid[:8])
    await process_callback_yandex(redis=redis, hgramid=hgramid, query_url=url)
    return '<html><head><style>body { color: green; }</style></head><body><h1>Success! Return to <a href="https://t.me/thatsoundbot">@thatsoundbot</a></h1></body></html>'
