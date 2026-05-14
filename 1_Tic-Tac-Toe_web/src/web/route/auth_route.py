from flask import Blueprint, jsonify, request 

from di.container import Container 
from domain.model.sign_up_request import SignUpRequest  
from domain.service.auth_service import AuthError  


def create_auth_blueprint(container: Container) -> Blueprint:  # создаёт Blueprint 
    blueprint = Blueprint("auth", __name__)  # создаём blueprint с именем "auth"

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

    # контроллер авторизации, endpoint авторизации 
    @blueprint.route("/auth/login", methods=["POST"])  
    def login():
        try:
            user_id = container.auth_service.authorize(  # проверяем заголовок Authorization через auth_service
                request.headers.get("Authorization", "")  # берём заголовок Authorization (если нет — пустая строка)
            )
            return jsonify({"user_id": user_id}), 200  # если авторизация успешна — возвращаем user_id
        except AuthError as exc:  # неверные креды/ошибка авторизации
            return jsonify({"error": str(exc)}), 401  # не авторизован
        except Exception:  # любые другие ошибки
            return jsonify({"error": "Internal server error."}), 500  # ошибка сервера

    return blueprint  # возвращаем настроенный blueprint, чтобы его зарегистрировали в Flask app