from pydantic import BaseModel


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class SocialLoginRequest(BaseModel):
    token: str