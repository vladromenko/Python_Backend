from dataclasses import dataclass

# модель RefreshJwtRequest, у которой есть refreshToken
@dataclass(frozen=True)
class RefreshJwtRequest:
    refresh_token: str
