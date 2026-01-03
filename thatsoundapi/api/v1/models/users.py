
from pydantic import BaseModel, Field


class UserIntegrationsResponse(BaseModel):
    """User integrations status."""

    spotify: bool = Field(default=False, description="Spotify integration status")
