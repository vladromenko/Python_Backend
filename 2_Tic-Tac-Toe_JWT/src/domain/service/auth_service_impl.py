from domain.model.jwt_request import JwtRequest
from domain.model.jwt_response import JwtResponse
from domain.model.sign_up_request import SignUpRequest
from domain.service.auth_service import AuthError, AuthService
from domain.service.jwt_provider import JwtError, JwtProvider
from domain.service.user_service import UserService

 # сервис авторизации обновлен для Jwt
class AuthServiceImpl(AuthService):
    def __init__(self, user_service: UserService, jwt_provider: JwtProvider) -> None:
        self._user_service = user_service
        self._jwt_provider = jwt_provider

    def register(self, request: SignUpRequest) -> bool:
        self._user_service.create_user(request)
        return True

    def authorize(self, request: JwtRequest) -> JwtResponse: # авторизация теперь использует jwt
        if (
            not isinstance(request.login, str)
            or not request.login
            or not isinstance(request.password, str)
            or not request.password
        ):
            raise AuthError("Login and password are required.")
        user = self._user_service.validate_credentials(request.login, request.password) # проверяем login/password
        if user is None:
            raise AuthError("Invalid login or password.")
        return self._build_response(user.user_id, rotate_refresh=True) # возвращаем JwtResponse 

    def refresh_access_token(self, refresh_token: str) -> JwtResponse:
        user_id = self._validate_and_get_user_id(refresh_token)
        return self._build_response(user_id, rotate_refresh=False, refresh_token=refresh_token)

    def refresh_refresh_token(self, refresh_token: str) -> JwtResponse: # метод обновления токена
        user_id = self._validate_and_get_user_id(refresh_token)
        return self._build_response(user_id, rotate_refresh=True)

    def _validate_and_get_user_id(self, refresh_token: str) -> str:
        try:
            self._jwt_provider.validate_refresh_token(refresh_token)
            user_id = self._jwt_provider.get_user_id(refresh_token)
        except JwtError as exc:
            raise AuthError(str(exc)) from exc
        user = self._user_service.get_user(user_id)
        if user is None:
            raise AuthError("User not found.")
        return user_id

    def _build_response(
        self, user_id: str, rotate_refresh: bool, refresh_token: str | None = None
    ) -> JwtResponse:
        user = self._user_service.get_user(user_id) # получаем пользователя по id
        if user is None:
            raise AuthError("User not found.")
        access_token = self._jwt_provider.generate_access_token(user) # генерируем новый access token
        if rotate_refresh:
            refresh = self._jwt_provider.generate_refresh_token(user) # генерируем новый refresh token
        else:
            if not refresh_token:
                raise AuthError("Refresh token is required.")
            refresh = refresh_token
        return JwtResponse(
            token_type="Bearer",
            access_token=access_token,
            refresh_token=refresh,
        )
