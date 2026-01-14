from enum import StrEnum
from typing import Any, Optional

import httpx
from loguru import logger

from thatsoundapi.utils.retry import retry_policy


class MethodEnum(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"



class HttpClient:
    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    def startup(cls) -> None:
        if cls._client is not None:
            return

        cls._client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
            ),
        )

        logger.info("HTTP client initialized")

    @classmethod
    async def shutdown(cls) -> None:
        if cls._client is None:
            return

        await cls._client.aclose()
        cls._client = None

        logger.info("HTTP client closed")

    @classmethod
    @retry_policy
    async def request(
        cls,
        method: MethodEnum,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        if cls._client is None:
            raise RuntimeError("HttpClient is not initialized")

        logger.debug("{method} {url}", method=method.value, url=url)

        response = await cls._client.request(
            method=method.value,
            url=url,
            **kwargs,
        )

        if response.status_code >= 400:
            logger.warning(
                "HTTP {status} from {url}",
                status=response.status_code,
                url=url,
            )

        return response

    @classmethod
    async def get(cls, url: str, **kwargs: Any) -> httpx.Response:
        return await cls.request(MethodEnum.GET, url, **kwargs)

    @classmethod
    async def post(cls, url: str, **kwargs: Any) -> httpx.Response:
        return await cls.request(MethodEnum.POST, url, **kwargs)

    @classmethod
    async def put(cls, url: str, **kwargs: Any) -> httpx.Response:
        return await cls.request(MethodEnum.PUT, url, **kwargs)
