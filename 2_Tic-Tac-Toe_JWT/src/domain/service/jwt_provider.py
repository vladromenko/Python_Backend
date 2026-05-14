from abc import ABC, abstractmethod

from domain.model.user import User


class JwtError(Exception):
    pass

# провайдер токенов
class JwtProvider(ABC):
    @abstractmethod
    def generate_access_token(self, user: User) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_refresh_token(self, user: User) -> str:
        raise NotImplementedError

    @abstractmethod
    def validate_access_token(self, token: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def validate_refresh_token(self, token: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_user_id(self, token: str) -> str:
        raise NotImplementedError
