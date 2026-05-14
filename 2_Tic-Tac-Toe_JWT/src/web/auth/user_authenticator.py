from functools import wraps

from flask import g, jsonify, request # jsonify превращает dict/list в json

from domain.service.jwt_provider import JwtError, JwtProvider


class UserAuthenticator:
    def __init__(self, jwt_provider: JwtProvider) -> None:
        self._jwt_provider = jwt_provider

    def protect(self, handler):
        @wraps(handler)
        def wrapper(*args, **kwargs):
            try:
                access_token = _extract_bearer_token(
                    request.headers.get("Authorization", "")
                )
                self._jwt_provider.validate_access_token(access_token)
                user_id = self._jwt_provider.get_user_id(access_token)
            except JwtError as exc:
                return jsonify({"error": str(exc)}), 401

            g.current_user_id = user_id
            return handler(*args, **kwargs)

        return wrapper


def _extract_bearer_token(authorization_header: str) -> str:
    if not authorization_header:
        raise JwtError("Missing authorization header.")
    header = authorization_header.strip()
    if not header.lower().startswith("bearer "):
        raise JwtError("Authorization header must be Bearer token.")
    token = header[7:].strip()
    if not token:
        raise JwtError("Access token is required.")
    return token
