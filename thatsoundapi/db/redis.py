
from contextvars import Token
from typing import Any, Awaitable

import redis.asyncio as redis
from loguru import logger

from thatsoundapi.core.spotify.models import SpotifyTokens
from thatsoundapi.core.yandex.models import YandexToken
from thatsoundapi.db.connection import redis_client as redis_client_var
from thatsoundapi.settings import get_settings


class RedisClient:
    """Redis client for async operations"""

    def __init__(self) -> None:
        """Initialize Redis client instance."""
        self._instance_client: redis.Redis | None = None  # Instance-level client
        self._token: Token["RedisClient | None"] | None = None  # ContextVar token

    async def __aenter__(self) -> "RedisClient":
        """Enter Redis client context and create instance session."""
        if self._instance_client is None:
            try:
                settings = get_settings()
                self._instance_client = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                )
                await self._instance_client.ping()
            except Exception as e:
                logger.exception("Failed to create Redis instance session", error=str(e))
                raise
        # Set in ContextVar for access without passing as parameter
        self._token = redis_client_var.set(self)
        return self

    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: object | None,
    ) -> None:
        """Exit Redis client context and close instance session."""
        if self._instance_client is not None:
            try:
                await self._instance_client.aclose()
                self._instance_client = None
            except Exception as e:
                logger.exception("Error during Redis instance session close", error=str(e))
                raise
        # Reset ContextVar
        if self._token is not None:
            redis_client_var.reset(self._token)

    def _ensure_instance_connected(self) -> redis.Redis:
        """Ensure instance-level client is connected."""
        if self._instance_client is None:
            raise RuntimeError("Redis instance client is not connected. Use async context manager.")
        return self._instance_client

    @classmethod
    def current(cls) -> "RedisClient":
        """Get current Redis client instance from context."""
        instance = redis_client_var.get()
        if instance is None:
            raise RuntimeError(
                "Redis client is not available in context. "
                "Make sure to use Depends(get_redis) in your route handler."
            )
        return instance

    # Instance methods for use with Depends(get_redis)
    async def has_spotify_integration(self, hgramid: str) -> bool:
        """Check if user has Spotify integration (instance method)."""
        client = self._ensure_instance_connected()
        key = f"spotify:tokens:{hgramid}"
        result = await client.exists(key)
        return bool(result > 0)

    async def has_yandex_music_integration(self, hgramid: str) -> bool:
        """Check if user has Yandex Music integration (instance method)."""
        client = self._ensure_instance_connected()
        key = f"yandex:token:{hgramid}"
        result = await client.exists(key)
        return bool(result > 0)

    async def save_spotify_oauth_state(self, hgramid: str, state: str, ttl: int) -> None:
        """Save Spotify OAuth state (instance method)."""
        client = self._ensure_instance_connected()
        key = f"spotify:oauth:state:{state}"
        await client.setex(key, ttl, hgramid)

    async def get_spotify_oauth_state(self, state: str) -> str | None:
        """Get Spotify OAuth state (instance method)."""
        client = self._ensure_instance_connected()
        key = f"spotify:oauth:state:{state}"
        result = await client.get(key)
        return str(result) if result is not None else None

    async def delete_spotify_oauth_state(self, state: str) -> None:
        """Delete Spotify OAuth state (instance method)."""
        client = self._ensure_instance_connected()
        key = f"spotify:oauth:state:{state}"
        await client.delete(key)

    async def save_spotify_tokens(self, hgramid: str, tokens: SpotifyTokens) -> None:
        """Save Spotify tokens (instance method)."""
        client = self._ensure_instance_connected()
        key = f"spotify:tokens:{hgramid}"
        result = client.hset(name=key, mapping=tokens.model_dump())
        if isinstance(result, Awaitable):
            await result

    async def get_spotify_tokens(self, hgramid: str) -> dict[str, Any] | None:
        """Get Spotify tokens (instance method)."""
        client = self._ensure_instance_connected()
        key = f"spotify:tokens:{hgramid}"
        result = client.hgetall(key)
        tokens_dict: dict[str, Any] | None = await result if isinstance(result, Awaitable) else result
        return tokens_dict if tokens_dict is not None else None

    async def get_yandex_token(self, hgramid: str) -> dict[str, Any] | None:
        """Get Yandex token (instance method)."""
        client = self._ensure_instance_connected()
        key = f"yandex:token:{hgramid}"
        result = client.hgetall(key)
        token_dict: dict[str, Any] | None = await result if isinstance(result, Awaitable) else result
        return token_dict if token_dict is not None else None

    async def save_yandex_token(self, hgramid: str, token: YandexToken) -> None:
        """Save Yandex token (instance method)."""
        client = self._ensure_instance_connected()
        key = f"yandex:token:{hgramid}"
        result = client.hset(name=key, mapping=token.model_dump())
        if isinstance(result, Awaitable):
            await result

    async def delete_yandex_token(self, hgramid: str) -> None:
        """Delete Yandex token (instance method)."""
        client = self._ensure_instance_connected()
        key = f"yandex:token:{hgramid}"
        await client.delete(key)
