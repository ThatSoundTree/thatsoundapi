from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Integrations(BaseModel):
    """User integrations status."""

    spotify: bool = Field(default=False, description="Spotify integration status")


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    htelegram_id: str = Field(..., description="Telegram user ID")
    created_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the user was created"
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the user was last updated"
    )
    integrations: Integrations = Field(
        default_factory=Integrations, description="User integrations status"
    )
