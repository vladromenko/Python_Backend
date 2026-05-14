from flask import Blueprint, jsonify
from flask import g

from di.container import Container

# поддержка пользователя в слое web
def create_user_blueprint(container: Container) -> Blueprint:  # фабрика: создаёт blueprint для user-роутов
    blueprint = Blueprint("user", __name__)  # создаём blueprint с именем "user"
    auth = container.user_authenticator  # берём компонент авторизации (проверяет пользователя)

    @blueprint.route("/users/<user_id>", methods=["GET"])  # endpoint получения пользователя по UUID
    @auth.protect  # защита: без авторизации нельзя (обычно выставляет g.current_user_id)
    def get_user(user_id: str):  # обработчик запроса GET /users/<user_id>
        try:
            user = container.user_service.get_user(user_id)  # вызываем сервис (внутри будет запрос в БД через репозиторий)
            if user is None:  # если пользователя нет
                return jsonify({"error": "User not found."}), 404  # 404 Not Found
            return jsonify({"user_id": user.user_id, "login": user.login}), 200  # отдаём публичные данные (без password_hash)
        except Exception:  # любые неожиданные ошибки
            return jsonify({"error": "Internal server error."}), 500  # 500 Server Error

    @blueprint.route("/users/me", methods=["GET"])
    @auth.protect
    def get_current_user():
        try:
            user = container.user_service.get_user(g.current_user_id)
            if user is None:
                return jsonify({"error": "User not found."}), 404
            return jsonify({"user_id": user.user_id, "login": user.login}), 200
        except Exception:
            return jsonify({"error": "Internal server error."}), 500

    return blueprint  # возвращаем blueprint для регистрации во Flask app
