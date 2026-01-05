
from pydantic import BaseModel


class SpotifyTokens(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str
    expires_at: int
