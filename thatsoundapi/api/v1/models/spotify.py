from typing import List, Optional

from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    """Status response model for Spotify operations"""

    htelegram_id: str = Field(..., description="Hashed Telegram user ID (first 8 characters)")
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Status message")


class TokenRefreshResponse(BaseModel):
    """Token refresh response model"""

    htelegram_id: str = Field(..., description="Hashed Telegram user ID (first 8 characters)")
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Status message")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class SpotifyTrack(BaseModel):
    """Spotify track model for recently played tracks."""

    id: str = Field(..., description="Spotify track ID")
    name: str = Field(..., description="Track name")
    artists: List[str] = Field(..., description="List of artist names")
    album_cover_url: Optional[str] = Field(default=None, description="Album cover image URL")
    # external_urls: Optional[str] = Field(default=None, description="Spotify track URL")
    played_at: Optional[str] = Field(default=None, description="ISO timestamp when track was played")


class RecentTracksResponse(BaseModel):
    """Response model for recently played tracks."""

    tracks: List[SpotifyTrack] = Field(..., description="List of recently played tracks")
