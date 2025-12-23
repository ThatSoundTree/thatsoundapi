from thatsoundapi.db.redis import RedisClient


class SpotifyRepository:
    """Repository for Spotify-related Redis operations"""

    @staticmethod
    async def save_spotify_tokens(
        htelegram_id: str,
        access_token: str,
        refresh_token: str,
        expires_in: int,
        token_type: str = "Bearer",
    ) -> None:
        await RedisClient.save_spotify_tokens(
            htelegram_id=htelegram_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            token_type=token_type,
        )

    @staticmethod
    async def get_spotify_tokens(htelegram_id: str) -> dict | None:
        return await RedisClient.get_spotify_tokens(htelegram_id)

    @staticmethod
    async def update_spotify_access_token(
        htelegram_id: str,
        access_token: str,
        expires_in: int,
    ) -> None:
        await RedisClient.update_spotify_access_token(
            htelegram_id=htelegram_id,
            access_token=access_token,
            expires_in=expires_in,
        )

    @staticmethod
    async def delete_spotify_tokens(htelegram_id: str) -> None:
        await RedisClient.delete_spotify_tokens(htelegram_id)

    @staticmethod
    async def has_valid_spotify_tokens(htelegram_id: str) -> bool:
        return await RedisClient.has_valid_spotify_tokens(htelegram_id)

    @staticmethod
    async def save_oauth_state(state: str, htelegram_id: str, ttl: int = 600) -> None:
        await RedisClient.save_oauth_state(state, htelegram_id, ttl)

    @staticmethod
    async def get_oauth_state(state: str) -> str | None:
        return await RedisClient.get_oauth_state(state)

    @staticmethod
    async def delete_oauth_state(state: str) -> None:
        await RedisClient.delete_oauth_state(state)
