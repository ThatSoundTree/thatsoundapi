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
    SECRET_KEY: SecretStr

    # Spotify API Configuration
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: SecretStr
    SPOTIFY_REDIRECT_URI: str
    SPOTIFY_REFRESH_TOKEN_TTL: int = Field(default=5184000, gt=0)
    ACCESS_TOKEN_EXP: int = Field(default=3600, gt=0)
    REFRESH_TOKEN_EXP: int = Field(default=604800, gt=0)

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = Field(default=6379, ge=1, le=65535)
    REDIS_DB: int = Field(default=0, ge=0)
    REDIS_PASSWORD: SecretStr | None = None

    # Logging Configuration
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

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

        if self.REDIS_PASSWORD is not None:
            password = quote_plus(self.REDIS_PASSWORD.get_secret_value())
            return f"redis://:{password}@{host}:{port}/{db}"
        return f"redis://{host}:{port}/{db}"


@lru_cache
def get_settings() -> Settings:
    """Cached settings function"""
    return Settings()  # type: ignore[call-arg]
