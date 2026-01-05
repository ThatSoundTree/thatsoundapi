import time

from pydantic import BaseModel, Field, model_validator


class SpotifyTokens(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str
    expires_at: int | None = Field(default=None)

    @model_validator(mode="after")
    def set_expires_at(self) -> "SpotifyTokens":
        self.expires_at = int(time.time()) + self.expires_in
        return self
