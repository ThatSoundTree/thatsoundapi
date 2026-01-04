from enum import StrEnum

import httpx
from loguru import logger


class MethodEnum(StrEnum):
    GET = "GET"
    POST = "POST"


class HttpClient:

    @staticmethod
    async def __any_method(method: MethodEnum, url: str, **kwargs: dict) -> httpx.Response:
        logger.debug("{method} {url}", method=method, url=url)

        async with httpx.AsyncClient() as client:
            if method == MethodEnum.GET:
                response = await client.get(url, **kwargs)
            elif method == MethodEnum.POST:
                response = await client.post(url, **kwargs)
            else:
                raise NotImplementedError

        return response

    @staticmethod
    async def get(url: str, **kwargs: dict) -> httpx.Response:
        return await HttpClient.__any_method(method=MethodEnum.GET, url=url, **kwargs)

    @staticmethod
    async def post(url: str, **kwargs: dict) -> httpx.Response:
        return await HttpClient.__any_method(method=MethodEnum.POST, url=url, **kwargs)
