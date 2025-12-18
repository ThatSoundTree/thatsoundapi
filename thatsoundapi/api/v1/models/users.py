from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    htelegram_id: str = Field(..., description="Telegram user ID")
    created_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the user was created"
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the user was last updated"
    )
