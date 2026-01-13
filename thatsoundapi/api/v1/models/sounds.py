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


class TrackView(BaseModel):
    provider: int
    id: str = Field(..., description="Spotify track ID")
    name: str = Field(..., description="Track name")
    artists: list[str] = Field(..., description="List of artist names")
    album_cover_url: Optional[str] = Field(default=None, description="Album cover image URL")
    url: Optional[str] = Field(default=None, description="Spotify track URL")


class Scrobble(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Scrobble ID")
    track_id: UUID = Field(..., description="Reference to track")
    listener_id: str = Field(..., description="Reference to user (Telegram ID)")


class IntegrationsTracks(BaseModel):
    spotify: list[TrackView]
    yandex_music: list[TrackView]


class RecentTracksResponse(BaseModel):
    """Response model for recently played tracks."""

    tracks: IntegrationsTracks = Field(..., description="List of recently played tracks")
