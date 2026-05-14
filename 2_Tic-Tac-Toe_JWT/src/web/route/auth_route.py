from flask import Blueprint, g, jsonify, request

from di.container import Container 
from domain.model.jwt_request import JwtRequest
from domain.model.refresh_jwt_request import RefreshJwtRequest
from domain.model.sign_up_request import SignUpRequest  
from domain.service.auth_service import AuthError  


def create_auth_blueprint(container: Container) -> Blueprint:  # создаёт Blueprint 
    blueprint = Blueprint("auth", __name__)  # создаём blueprint с именем "auth"
    auth = container.user_authenticator

    # контроллер авторизации, endpoint регистрации
    @blueprint.route("/auth/signup", methods=["POST"])  
    def signup():
        try:
            data = request.get_json(silent=True)  # читаем JSON-тело запроса -> dict или None
            if not isinstance(data, dict):  # проверяем, что пришёл именно объект JSON (словарь)
                raise ValueError("Invalid JSON body.")
            login = data.get("login")  # достаём login из JSON
            password = data.get("password")  # достаём password из JSON
            signup_request = SignUpRequest(login=login, password=password)  # упаковываем данные в доменную модель запроса
            container.auth_service.register(signup_request)  # вызываем сервис регистрации (там будет запись в БД)
            return jsonify({"success": True}), 201  # успешная регистрация
        except ValueError as exc:  # ошибки валидации/формата данных
            return jsonify({"error": str(exc)}), 400  # неверный запрос
        except Exception:  # любые другие ошибки
            return jsonify({"error": "Internal server error."}), 500  # ошибка сервера

    # обновлен контроллер авторизации, endpoint авторизации 
    @blueprint.route("/auth/login", methods=["POST"])  
    def login():
        try:
            data = request.get_json(silent=True)
            if not isinstance(data, dict):
                raise ValueError("Invalid JSON body.")
            jwt_request = JwtRequest(
                login=data.get("login"),
                password=data.get("password"),
            )
            response = container.auth_service.authorize(jwt_request)
            return jsonify(_jwt_response_to_dict(response)), 200
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except AuthError as exc:  # неверные креды/ошибка авторизации
            return jsonify({"error": str(exc)}), 401  # не авторизован
        except Exception:  # любые другие ошибки
            return jsonify({"error": "Internal server error."}), 500  # ошибка сервера

    @blueprint.route("/auth/access-token", methods=["POST"])
    def refresh_access_token():
        try:
            refresh_request = _parse_refresh_request(request.get_json(silent=True))
            response = container.auth_service.refresh_access_token(
                refresh_request.refresh_token
            )
            return jsonify(_jwt_response_to_dict(response)), 200
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except AuthError as exc:
            return jsonify({"error": str(exc)}), 401
        except Exception:
            return jsonify({"error": "Internal server error."}), 500

    @blueprint.route("/auth/refresh-token", methods=["POST"])
    def refresh_refresh_token():
        try:
            refresh_request = _parse_refresh_request(request.get_json(silent=True))
            response = container.auth_service.refresh_refresh_token(
                refresh_request.refresh_token
            )
            return jsonify(_jwt_response_to_dict(response)), 200
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except AuthError as exc:
            return jsonify({"error": str(exc)}), 401
        except Exception:
            return jsonify({"error": "Internal server error."}), 500

    @blueprint.route("/auth/me", methods=["GET"])
    @auth.protect
    def get_current_user():
        try:
            user = container.user_service.get_user(g.current_user_id)
            if user is None:
                return jsonify({"error": "User not found."}), 404
            return jsonify({"user_id": user.user_id, "login": user.login}), 200
        except Exception:
            return jsonify({"error": "Internal server error."}), 500

    return blueprint  # возвращаем настроенный blueprint, чтобы его зарегистрировали в Flask app


def _parse_refresh_request(data) -> RefreshJwtRequest:
    if not isinstance(data, dict):
        raise ValueError("Invalid JSON body.")
    refresh_token = data.get("refreshToken") or data.get("refresh_token")
    if not isinstance(refresh_token, str) or not refresh_token:
        raise ValueError("refreshToken is required.")
    return RefreshJwtRequest(refresh_token=refresh_token)


def _jwt_response_to_dict(response) -> dict: # превращаем ответ в json словарь
    return {
        "type": response.token_type,
        "accessToken": response.access_token,
        "refreshToken": response.refresh_token,
    }
