import uuid
from datetime import datetime
from sqlalchemy import DateTime, String, func, ForeignKey
from sqlalchemy.dialects.postgresql.base import UUID, SMALLINT, TEXT
from sqlalchemy.orm import Mapped, mapped_column

from thatsoundapi.db.base import Base


class User(Base):
    """User database model"""

    __tablename__ = "users"

    hgramid: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        index=True,
        comment="Hashed Telegram user ID",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the user was created",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when the user was last updated",
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(hgramid='{self.htelegram_id[:8]}...')>"



class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id: Mapped[SMALLINT] = mapped_column(SMALLINT, ForeignKey("track_providers.id", ondelete="CASCADE"), nullable=False)
    external_id: Mapped[TEXT] = mapped_column(TEXT, nullable=False)
    tfile_url: Mapped[TEXT] = mapped_column(TEXT, nullable=True)

    def as_dict(self) -> dict:
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, uuid.UUID):
                value = str(value)
            result[column.name] = value
        return result


class Scrobble(Base):
    __tablename__ = "scrobbles"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    track_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False)
    listener_id: Mapped[String] = mapped_column(String, ForeignKey("users.hgramid", ondelete="CASCADE"), nullable=False)
