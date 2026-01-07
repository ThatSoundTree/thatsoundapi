import time
from urllib.parse import parse_qs, urlparse

from loguru import logger

from thatsoundapi.core.yandex.models import YandexToken
from thatsoundapi.core.yandex.oauth import check_and_save_token
# from thatsoundapi.core.yandex.oauth import is_token_alive
from thatsoundapi.db.redis import RedisClient


def extract_token_data(hgramid: str, yandex_url: str) -> YandexToken:
    parsed_url = urlparse(yandex_url)
    fragment = parsed_url.fragment
    raw_params = parse_qs(fragment, strict_parsing=True)

    params = {
        key: values[0] if values else ""
        for key, values in raw_params.items()
    }

    expires_in = int(params["expires_in"])

    logger.info("[{hgramid}] [yandex] token got", hgramid=hgramid[:8])

    return YandexToken(
        access_token=params["access_token"],
        token_type=params["token_type"],
        expires_in=expires_in,
        expires_at=int(time.time()) + expires_in,
    )


async def process_callback(hgramid: str, query_url: str):
    await RedisClient.delete_yandex_token(hgramid=hgramid)
    yandex_token = extract_token_data(hgramid=hgramid, yandex_url=query_url)
    await check_and_save_token(hgramid=hgramid, token=yandex_token)
