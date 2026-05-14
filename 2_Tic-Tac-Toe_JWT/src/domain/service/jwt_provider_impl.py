from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from domain.model.user import User
from domain.service.jwt_provider import JwtError, JwtProvider


class JwtProviderImpl(JwtProvider):
    def generate_access_token(self, user: User) -> str: # генерация токена с сохранением UUID
        return create_access_token(identity=user.user_id)

    def generate_refresh_token(self, user: User) -> str: # генерация токена с сохранением UUID
        return create_refresh_token(identity=user.user_id)

    def validate_access_token(self, token: str) -> None: # валидация 
        payload = _decode(token)
        if payload.get("type") != "access": # в токене лежат sub - user_id, type - тип токена, exp - время истечения срока токена
            raise JwtError("Invalid access token.")

    def validate_refresh_token(self, token: str) -> None:
        payload = _decode(token)
        if payload.get("type") != "refresh":
            raise JwtError("Invalid refresh token.")

    def get_user_id(self, token: str) -> str: # извлечение UUID из токена
        payload = _decode(token)
        user_id = payload.get("sub") # sub это user_id 
        if not isinstance(user_id, str) or not user_id:
            raise JwtError("Token does not contain user id.")
        return user_id


def _decode(token: str) -> dict:
    if not token or not isinstance(token, str):
        raise JwtError("Token is required.")
    try:
        return decode_token(token)  # JWT выглядит как header.payload.signature, decode проверяет, что signature вычислена моим сервером и ей нужен ключ валидации (JWT_SECRET_KEY)
    except ExpiredSignatureError as exc:
        raise JwtError("Token has expired.") from exc
    except InvalidTokenError as exc:
        raise JwtError("Invalid token.") from exc
    except Exception as exc:
        raise JwtError("Invalid token.") from exc
