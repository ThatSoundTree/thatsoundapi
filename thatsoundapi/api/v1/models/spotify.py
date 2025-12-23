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
    album: Optional[str] = Field(default=None, description="Album name")
    album_cover_url: Optional[str] = Field(default=None, description="Album cover image URL")
    external_urls: Optional[str] = Field(default=None, description="Spotify track URL")
    played_at: Optional[str] = Field(default=None, description="ISO timestamp when track was played")
    duration_ms: Optional[int] = Field(default=None, description="Track duration in milliseconds")
    preview_url: Optional[str] = Field(default=None, description="Preview audio URL")


class RecentTracksResponse(BaseModel):
    """Response model for recently played tracks."""

    htelegram_id: str = Field(..., description="Hashed Telegram user ID (first 8 characters)")
    tracks: List[SpotifyTrack] = Field(..., description="List of recently played tracks")
    count: int = Field(..., description="Number of tracks returned")
