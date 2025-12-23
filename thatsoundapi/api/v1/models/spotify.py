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
