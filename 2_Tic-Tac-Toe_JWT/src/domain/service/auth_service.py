from abc import ABC, abstractmethod

from domain.model.jwt_request import JwtRequest
from domain.model.jwt_response import JwtResponse
from domain.model.sign_up_request import SignUpRequest


class AuthError(Exception):
    pass


class AuthService(ABC):
    @abstractmethod
    def register(self, request: SignUpRequest) -> bool:
        raise NotImplementedError

    @abstractmethod
    def authorize(self, request: JwtRequest) -> JwtResponse:
        raise NotImplementedError

    @abstractmethod
    def refresh_access_token(self, refresh_token: str) -> JwtResponse:
        raise NotImplementedError

    @abstractmethod
    def refresh_refresh_token(self, refresh_token: str) -> JwtResponse:
        raise NotImplementedError
