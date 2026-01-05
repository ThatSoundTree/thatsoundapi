from typing import Literal

import redis.asyncio as redis
from loguru import logger

from thatsoundapi.services.spotify.models import SpotifyTokens
from thatsoundapi.settings import get_settings


class RedisClient:
    """Redis client singleton for async operations"""

    _instance: "RedisClient | None" = None
    _client: redis.Redis | None = None

    def __new__(cls) -> "RedisClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def connect(cls) -> None:
        if cls._client is None:
            try:
                settings = get_settings()
                cls._client = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                )
                await cls._client.ping()
                logger.info("Redis connection established", url=settings.REDIS_HOST)
            except Exception as e:
                logger.exception("Failed to connect to Redis", error=str(e))
                raise

    @classmethod
    async def disconnect(cls) -> None:
        if cls._client is not None:
            try:
                await cls._client.aclose()
                cls._client = None
                logger.info("Redis disconnected")
            except Exception as e:
                logger.exception("Error during Redis disconnect", error=str(e))
                raise

    @classmethod
    def _ensure_connected(cls) -> redis.Redis:
        if cls._client is None:
            raise RuntimeError("Redis client is not connected. Call RedisClient.connect() first.")
        return cls._client

    @classmethod
    async def has_spotify_integration(cls, hgramid: str) -> bool:
        client = cls._ensure_connected()
        key = f"spotify:tokens:{hgramid}"
        result = await client.exists(key)
        return bool(result > 0)

    @classmethod
    async def save_spotify_oauth_state(cls, hgramid: str, state: str,  ttl: int) -> None:
        client = cls._ensure_connected()
        key = f"spotify:oauth:state:{state}"
        await client.setex(key, ttl, hgramid)

    @classmethod
    async def get_spotify_oauth_state(cls, state: str) -> str | None:
        client = cls._ensure_connected()
        key = f"spotify:oauth:state:{state}"
        result = await client.get(key)
        return str(result) if result is not None else None

    @classmethod
    async def delete_spotify_oauth_state(cls, state: str) -> None:
        client = cls._ensure_connected()
        key = f"spotify:oauth:state:{state}"
        await client.delete(key)

    @classmethod
    async def save_spotify_tokens(cls, hgramid: str, tokens: SpotifyTokens) -> None:
        client = cls._ensure_connected()
        key = f"spotify:tokens:{hgramid}"
        await client.hset(name=key, mapping=tokens.model_dump())

    @classmethod
    async def get_spotify_tokens(cls, hgramid: str) -> dict | None:
        client = cls._ensure_connected()
        key = f"spotify:tokens:{hgramid}"
        tokens_dict = await client.hgetall(key)
        return tokens_dict if tokens_dict is not None else None



    @classmethod
    async def check_revoked_token(cls, jti: str, token_type: Literal["access", "refresh"] = "access") -> bool:
        client = cls._ensure_connected()
        key = f"jti:{token_type}:{jti}"
        result = await client.exists(key)
        return bool(result > 0)

    @classmethod
    async def revoke_token(
        cls,
        jti: str,
        ttl: int | None = None,
        token_type: Literal["access", "refresh"] = "access",
    ) -> None:
        client = cls._ensure_connected()
        settings = get_settings()

        key = f"jti:{token_type}:{jti}"
        ttl = ttl or settings.ACCESS_TOKEN_EXP

        await client.setex(key, ttl, jti)

    @classmethod
    async def set(
        cls,
        key: str,
        value: str,
        ttl: int | None = None,
    ) -> None:
        client = cls._ensure_connected()
        if ttl is not None:
            await client.setex(key, ttl, value)
        else:
            await client.set(key, value)

    @classmethod
    async def get(cls, key: str) -> str | None:
        client = cls._ensure_connected()
        result = await client.get(key)
        return str(result) if result is not None else None

    @classmethod
    async def delete(cls, key: str) -> None:
        client = cls._ensure_connected()
        await client.delete(key)

    @classmethod
    async def exists(cls, key: str) -> bool:
        client = cls._ensure_connected()
        result = await client.exists(key)
        return bool(result > 0)






    @classmethod
    async def delete_spotify_tokens(cls, htelegram_id: str) -> None:
        logger.info("Deleting Spotify tokens", htelegram_id=htelegram_id[:8])
        try:
            client = cls._ensure_connected()
            key = f"spotify:tokens:{htelegram_id}"
            await client.delete(key)
            logger.success("Spotify tokens deleted", htelegram_id=htelegram_id[:8])
        except Exception as e:
            logger.exception("Failed to delete Spotify tokens", htelegram_id=htelegram_id[:8], error=str(e))
            raise

    @classmethod
    async def has_valid_spotify_tokens(cls, htelegram_id: str) -> bool:
        tokens = await cls.get_spotify_tokens(htelegram_id)
        if not tokens:
            return False

        refresh_token = tokens.get("refresh_token")
        return bool(refresh_token and isinstance(refresh_token, str) and refresh_token)
