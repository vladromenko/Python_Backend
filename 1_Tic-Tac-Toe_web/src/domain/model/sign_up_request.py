from dataclasses import dataclass

# модель SignUpRequest, у которой будет логин и пароль
@dataclass(frozen=True)  # неизменяемый объект
class SignUpRequest:  # модель данных запроса на регистрацию
    login: str  # логин, пришедший от клиента
    password: str  # пароль, пришедший от клиента (потом будет превращён в хэш)
