from dataclasses import dataclass

# модель Jwt, у которой есть логин и пароль
@dataclass(frozen=True)
class JwtRequest:
    login: str
    password: str
