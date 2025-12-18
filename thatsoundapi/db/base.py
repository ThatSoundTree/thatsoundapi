"""Database base configuration with engine, sessionmaker, and DI container."""

import punq  # type: ignore[import-untyped]
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from thatsoundapi.settings import get_settings

settings = get_settings()

# Create async engines
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)

# Create declarative base for models
Base = declarative_base()

# Create session makers
session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class SessionMaker:
    """Factory class for creating sessionmaker instances."""

    def __new__(cls) -> async_sessionmaker[AsyncSession]:  # type: ignore[misc]
        return async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )


# Dependency injection container
container = punq.Container()  # type: ignore[assignment]
container.register(async_sessionmaker, SessionMaker)  # type: ignore[arg-type]
