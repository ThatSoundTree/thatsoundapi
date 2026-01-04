import base64
from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings including database, Redis, Spotify, and authentication configuration"""

    # PostgreSQL Database Configuration
    POSTGRES_HOST: str
    POSTGRES_PORT: int = Field(ge=1, le=65535)
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr

    # Security
    TELEGRAM_HASH_KEY: SecretStr = Field(..., description="Secret key for hashing telegram_id to htelegram_id")

    # TSDirect API Configuration
    TO_DIRECT_AUTH_KEY: SecretStr = Field(..., description="Bearer token for authentication with thatsounddirect API")
    TSDIRECT_API_BASE_URL: str = Field(..., description="Base URL for TSDirect API")

    # Spotify API Configuration
    SPOTIFY_REFRESH_TOKEN_TTL: int = Field(default=5184000, gt=0)

    ACCESS_TOKEN_EXP: int = Field(default=3600, gt=0)
    REFRESH_TOKEN_EXP: int = Field(default=604800, gt=0)

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = Field(default=6379, ge=1, le=65535)
    REDIS_DB: int = Field(default=0, ge=0)
    REDIS_USERNAME: str | None = None
    REDIS_PASSWORD: SecretStr | None = None

    # Logging Configuration
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # Database Engine Configuration
    DB_ECHO: bool = Field(default=False, description="Enable SQL query logging")
    DB_POOL_SIZE: int = Field(default=10, ge=1, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, ge=0, description="Maximum overflow connections")

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore", env_prefix="BACKEND_"
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL(self) -> str:
        """Auto assembling postgres db url for asyncpg with URL encoding"""
        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD.get_secret_value())
        host = self.POSTGRES_HOST
        port = self.POSTGRES_PORT
        db = quote_plus(self.POSTGRES_DB)
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ALEMBIC_DATABASE_URL(self) -> str:
        """Auto assembling alembic db url for psycopg2 with URL encoding"""
        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD.get_secret_value())
        host = self.POSTGRES_HOST
        port = self.POSTGRES_PORT
        db = quote_plus(self.POSTGRES_DB)
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def REDIS_URL(self) -> str:
        """Auto assembling redis url with URL encoding"""
        host = self.REDIS_HOST
        port = self.REDIS_PORT
        db = self.REDIS_DB

        if self.REDIS_USERNAME and self.REDIS_PASSWORD:
            username = quote_plus(self.REDIS_USERNAME)
            password = quote_plus(self.REDIS_PASSWORD.get_secret_value())
            return f"redis://{username}:{password}@{host}:{port}/{db}"
        elif self.REDIS_USERNAME:
            username = quote_plus(self.REDIS_USERNAME)
            return f"redis://{username}@{host}:{port}/{db}"
        elif self.REDIS_PASSWORD:
            password = quote_plus(self.REDIS_PASSWORD.get_secret_value())
            return f"redis://:{password}@{host}:{port}/{db}"
        return f"redis://{host}:{port}/{db}"


class SpotifyIntegrationSettings(BaseSettings):
    """Something in the way."""


    CLIENT_ID: str
    CLIENT_SECRET: SecretStr
    REDIRECT_URI: str

    OAUTH_STATE_TTL: int = Field(default=600, gt=0)
    SCOPES: str = Field(default="user-read-recently-played streaming")
    AUTHORIZE_URL: str = Field(default="https://accounts.spotify.com/authorize")
    TOKEN_URL: str = Field(default="https://accounts.spotify.com/api/token")
    API_BASE_URL: str = Field(default="https://api.spotify.com/v1")

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore", env_prefix="SPOTIFY_"
    )

    def get_header(self) -> dict:
        credentials = f"{self.CLIENT_ID}:{self.CLIENT_SECRET.get_secret_value()}"
        return {
            "Authorization": f"Basic {base64.b64encode(credentials.encode()).decode()}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def get_exchange_payload(self, code: str) -> dict:
        return {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.REDIRECT_URI,
        }

    @classmethod
    def get_refresh_payload(self, refresh_token: str) -> dict:
        return {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }


@lru_cache
def get_settings() -> Settings:
    """Cached settings function"""
    return Settings()  # type: ignore[call-arg]


@lru_cache
def get_spotify_settings() -> SpotifyIntegrationSettings:
    """Cached spotify settings function"""
    return SpotifyIntegrationSettings()  # type: ignore[call-arg]
