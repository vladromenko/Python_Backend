from functools import wraps

from flask import g, jsonify, request # jsonify превращает dict/list в json

from domain.service.auth_service import AuthError, AuthService


# UserAuthenticator: валидация логина/пароля, при успехе идет запрос
class UserAuthenticator:  # защита роутов от неавторизованных
    def __init__(self, auth_service: AuthService) -> None:  # получаем сервис авторизации
        self._auth_service = auth_service  # сохраняем его

    def protect(self, handler):  # декоратор для endpoint
        @wraps(handler)  # сохраняем информацию о handler
        def wrapper(*args, **kwargs):  # обёртка вокруг endpoint
            try:
                # берём Authorization и проверяем логин/пароль
                user_id = self._auth_service.authorize(
                    request.headers.get("Authorization", "")
                )
            except AuthError as exc:
                # если не прошли проверку -> 401 и не вызываем handler
                return jsonify({"error": str(exc)}), 401

            # если прошли проверку -> сохраняем user_id для текущего запроса
            g.current_user_id = user_id
            # выполняем настоящий endpoint
            return handler(*args, **kwargs)

        return wrapper  # возвращаем защищённую версию endpoint