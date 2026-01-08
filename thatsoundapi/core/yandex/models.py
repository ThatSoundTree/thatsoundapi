from pydantic import BaseModel


class YandexToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    expires_at: int
    user_id: int | None = None
