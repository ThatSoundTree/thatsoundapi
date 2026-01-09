from sqlalchemy import select, insert
from uuid import UUID
from thatsoundapi.utils.exceptions.app import UnknownDatabaseError

from thatsoundapi.db.connection import db_session
from thatsoundapi.db.models import Track, Scrobble


class TracksRepository:
    """Track database operations."""

    @staticmethod
    async def get_by_external_id(external_id: str) -> Track | None:
        """Get track by external id."""

        session = db_session.get()
        if session is None:
            raise UnknownDatabaseError

        query = select(Track).where(Track.external_id == external_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(provider_id: int, external_id: str) -> Track:
        """Create a new user."""
        session = db_session.get()
        if session is None:
            raise UnknownDatabaseError
        query = insert(Track).values(provider_id=provider_id, external_id=external_id).returning(Track)
        result = await session.execute(query)
        track = result.scalars().first()
        if track is None:
            raise UnknownDatabaseError()
        return track


class ScrobblesRepository:
    """Scrobble database operations."""

    @staticmethod
    async def get(listener_id: str, track_id: UUID) -> Scrobble | None:
        """Get user srobble."""

        session = db_session.get()
        if session is None:
            raise UnknownDatabaseError

        query = select(Scrobble).where((Scrobble.listener_id == listener_id) & (Scrobble.track_id == track_id))
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(listener_id: str, track_id: UUID) -> Scrobble:
        """Create a new scrobble."""
        session = db_session.get()
        if session is None:
            raise UnknownDatabaseError
        query = insert(Scrobble).values(listener_id=listener_id, track_id=track_id).returning(Scrobble)
        result = await session.execute(query)
        scrobble = result.scalars().first()
        if scrobble is None:
            raise UnknownDatabaseError()
        return scrobble
