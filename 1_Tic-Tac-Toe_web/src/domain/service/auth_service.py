from abc import ABC, abstractmethod

from domain.model.sign_up_request import SignUpRequest


class AuthError(Exception):
    pass


class AuthService(ABC):
    @abstractmethod
    def register(self, request: SignUpRequest) -> bool:
        raise NotImplementedError

    @abstractmethod
    def authorize(self, authorization_header: str) -> str:
        raise NotImplementedError
