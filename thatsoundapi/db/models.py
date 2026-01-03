from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from thatsoundapi.db.base import Base


class User(Base):
    """User database model.

    Attributes:
        htelegram_id: Hashed Telegram user ID (primary key)
        created_at: Timestamp when the user was created
        updated_at: Timestamp when the user was last updated
    """

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
        return f"<User(htelegram_id='{self.htelegram_id[:8]}...')>"
