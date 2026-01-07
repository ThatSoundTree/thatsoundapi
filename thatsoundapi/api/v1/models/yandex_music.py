from typing import Optional

from pydantic import BaseModel, Field


class YandexMusicTrack(BaseModel):
    """Yandex music track model for recently played tracks."""

    id: str = Field(..., description="Yandex Music track ID")
    name: str = Field(..., description="Track name")
    artists: list[str] = Field(..., description="List of artist names")
    album_cover_url: Optional[str] = Field(default=None, description="Album cover image URL")
    url: Optional[str] = Field(default=None, description="Yandex Music track URL")
    played_at: Optional[str] = Field(default=None, description="ISO timestamp when track was played")
