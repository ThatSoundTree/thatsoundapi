from loguru import logger

from thatsoundapi.core.yandex.models import YandexToken
from thatsoundapi.db.redis import RedisService
from thatsoundapi.settings import get_yandex_settings
from thatsoundapi.utils.exceptions.yandex import YandexTokenError
from thatsoundapi.utils.http_client import HttpClient

async def get_user_id(hgramid:str, access_token: str) -> str | None:
    yandex_settings = get_yandex_settings()

    response = await HttpClient.get(
        url=f"{yandex_settings.API_BASE_URL}/account/status",
        headers=yandex_settings.get_header(access_token=access_token),
    )

    if response.status_code != 200:
        logger.error("[{hgramid}] [yandex] failed check: {error_text}", hgramid=hgramid[:8], error_text=response.text)
        return None

    resp = response.json()
    uid = resp.get("result", {}).get("account", {}).get("uid", None)
    return str(uid) if uid is not None else None


async def check_and_save_token(redis: RedisService, hgramid: str, token: YandexToken) -> None:
    user_id = await get_user_id(hgramid=hgramid, access_token=token.access_token)
    if not user_id:
        raise YandexTokenError

    token.user_id = int(user_id)
    logger.success("[{hgramid}] [yandex] saved tokens", hgramid=hgramid[:8])
    await redis.save_yandex_token(hgramid=hgramid, token=token)
