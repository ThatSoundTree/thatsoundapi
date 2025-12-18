from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TrackProvider(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Track provider ID")
    name: str = Field(..., max_length=15, description="Track provider name")


class Track(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Track ID")
    provider_id: int = Field(..., description="Reference to track provider")
    external_id: str = Field(..., description="External track ID from provider")
    tfile_url: Optional[str] = Field(default=None, description="Track file URL")


class Scrobble(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Scrobble ID")
    track_id: UUID = Field(..., description="Reference to track")
    listener_id: str = Field(..., description="Reference to user (Telegram ID)")
