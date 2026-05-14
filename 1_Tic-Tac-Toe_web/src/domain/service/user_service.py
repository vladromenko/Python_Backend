from abc import ABC, abstractmethod
from typing import Optional

from domain.model.sign_up_request import SignUpRequest
from domain.model.user import User


class UserService(ABC):
    @abstractmethod
    def create_user(self, request: SignUpRequest) -> User:
        raise NotImplementedError

    @abstractmethod
    def get_user(self, user_id: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def get_by_login(self, login: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def validate_credentials(self, login: str, password: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def ensure_computer_user(self) -> None:
        raise NotImplementedError
