from typing import Any, Awaitable
from thatsoundapi.core.spotify.models import SpotifyTokens
from thatsoundapi.core.yandex.models import YandexToken
from thatsoundapi.settings import get_settings

from typing import Optional
import redis.asyncio as redis
from loguru import logger



class RedisClient:
    _client: Optional[redis.Redis] = None

    @classmethod
    async def startup(cls) -> None:
        if cls._client is not None:
            return

        settings = get_settings()

        cls._client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )

        try:
            await cls._client.ping()
        except Exception:
            logger.exception("Failed to connect to Redis")
            raise

        logger.info("Redis client initialized")

    @classmethod
    async def shutdown(cls) -> None:
        if cls._client is None:
            return

        await cls._client.aclose()
        cls._client = None

        logger.info("Redis client closed")

    @classmethod
    def client(cls) -> redis.Redis:
        if cls._client is None:
            raise RuntimeError("Redis client is not initialized")
        return cls._client


class RedisService:

    def __init__(self, redis_client: redis.Redis) -> None:
        self._redis = redis_client

    async def has_spotify_integration(self, hgramid: str) -> bool:
        """Check if user has Spotify integration (instance method)."""
        return bool(await self._redis.exists(f"spotify:tokens:{hgramid}"))

    async def has_yandex_music_integration(self, hgramid: str) -> bool:
        """Check if user has Yandex Music integration (instance method)."""
        return bool(await self._redis.exists(f"yandex:token:{hgramid}"))

    async def save_spotify_oauth_state(self, hgramid: str, state: str, ttl: int) -> None:
        """Save Spotify OAuth state (instance method)."""
        key = f"spotify:oauth:state:{state}"
        await self._redis.setex(key, ttl, hgramid)

    async def get_spotify_oauth_state(self, state: str) -> str | None:
        """Get Spotify OAuth state (instance method)."""
        result = await self._redis.get(f"spotify:oauth:state:{state}")
        return str(result) if result is not None else None

    async def delete_spotify_oauth_state(self, state: str) -> None:
        """Delete Spotify OAuth state (instance method)."""
        await self._redis.delete(f"spotify:oauth:state:{state}")

    async def save_spotify_tokens(self, hgramid: str, tokens: SpotifyTokens) -> None:
        """Save Spotify tokens (instance method)."""
        result = self._redis.hset(name=f"spotify:tokens:{hgramid}", mapping=tokens.model_dump())
        if isinstance(result, Awaitable):
            await result

    async def get_spotify_tokens(self, hgramid: str) -> SpotifyTokens | None:
        """Get Spotify tokens (instance method)."""
        result = self._redis.hgetall(name=f"spotify:tokens:{hgramid}")
        tokens_dict: dict[str, Any] | None = await result if isinstance(result, Awaitable) else result
        if not tokens_dict:
            return None

        return SpotifyTokens.model_validate(tokens_dict)

    async def get_yandex_token(self, hgramid: str) -> YandexToken | None:
        """Get Yandex token (instance method)."""
        result = self._redis.hgetall(f"yandex:token:{hgramid}")
        token_dict: dict[str, Any] | None = await result if isinstance(result, Awaitable) else result
        if not token_dict:
            return None

        return YandexToken.model_validate(token_dict)

    async def save_yandex_token(self, hgramid: str, token: YandexToken) -> None:
        """Save Yandex token (instance method)."""
        result = self._redis.hset(name=f"yandex:token:{hgramid}", mapping=token.model_dump())
        if isinstance(result, Awaitable):
            await result

    async def delete_yandex_token(self, hgramid: str) -> None:
        """Delete Yandex token (instance method)."""
        await self._redis.delete(f"yandex:token:{hgramid}")
