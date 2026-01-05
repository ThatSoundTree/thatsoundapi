import httpx
from loguru import logger

from thatsoundapi.settings import get_settings


class TSDirectHTTPClient:
    """HTTP client for making authenticated requests to TSDirect API with Bearer token."""

    @staticmethod
    def _get_auth_headers() -> dict[str, str]:
        """Get authorization headers with Bearer token."""
        settings = get_settings()
        return {
            "Authorization": f"Bearer {settings.TO_DIRECT_AUTH_KEY.get_secret_value()}",
        }

    @staticmethod
    async def get(url: str, **kwargs) -> httpx.Response:
        """Make authenticated GET request to TSDirect API."""
        headers = TSDirectHTTPClient._get_auth_headers()
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers

        async with httpx.AsyncClient() as client:
            logger.debug("Making authenticated GET request", url=url)
            response = await client.get(url, **kwargs)
            return response

    @staticmethod
    async def post(url: str, **kwargs) -> httpx.Response:
        """Make authenticated POST request to TSDirect API."""
        headers = TSDirectHTTPClient._get_auth_headers()
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers

        async with httpx.AsyncClient() as client:
            logger.debug("Making authenticated POST request", url=url)
            response = await client.post(url, **kwargs)
            return response

    @staticmethod
    async def put(url: str, **kwargs) -> httpx.Response:
        """Make authenticated PUT request to TSDirect API."""
        headers = TSDirectHTTPClient._get_auth_headers()
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers

        async with httpx.AsyncClient() as client:
            logger.debug("Making authenticated PUT request", url=url)
            response = await client.put(url, **kwargs)
            return response

    @staticmethod
    async def delete(url: str, **kwargs) -> httpx.Response:
        """Make authenticated DELETE request to TSDirect API."""
        headers = TSDirectHTTPClient._get_auth_headers()
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers

        async with httpx.AsyncClient() as client:
            logger.debug("Making authenticated DELETE request", url=url)
            response = await client.delete(url, **kwargs)
            return response

    @staticmethod
    async def patch(url: str, **kwargs) -> httpx.Response:
        """Make authenticated PATCH request to TSDirect API."""
        headers = TSDirectHTTPClient._get_auth_headers()
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers

        async with httpx.AsyncClient() as client:
            logger.debug("Making authenticated PATCH request", url=url)
            response = await client.patch(url, **kwargs)
            return response
