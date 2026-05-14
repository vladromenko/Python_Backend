from dataclasses import dataclass  

# добавляем пользователей, у которых будет UUID, логин и пароль
@dataclass(frozen=True)  
class User:  # доменная модель пользователя 
    user_id: str  # идентификатор пользователя (UUID строкой)
    login: str  # логин пользователя
    password_hash: str  # хэш пароля 