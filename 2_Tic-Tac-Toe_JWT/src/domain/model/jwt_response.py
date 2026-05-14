from dataclasses import dataclass

# модель Jwt, у которой есть тип, access token и refresh token
@dataclass(frozen=True)
class JwtResponse:
    token_type: str
    access_token: str
    refresh_token: str
