import os
from datetime import timedelta

from flask import Flask
from flask_jwt_extended import JWTManager

from di.container import Container
from web.route.auth_route import create_auth_blueprint
from web.route.game_route import create_game_blueprint
from web.route.user_route import create_user_blueprint


def create_app(container: Container) -> Flask:
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    JWTManager(app)

    app.register_blueprint(create_auth_blueprint(container)) # регистрация и вход пользователя
    # signup -> создать нового пользователя
    # login -> проверить учетные данные и вернуть jwt-токены

    app.register_blueprint(create_game_blueprint(container))  # создание, подключение и ведение партии
    # games -> создать игру (с игроком или компьютером)
    # games/available -> получить игры в ожидании второго игрока
    # games/<game_id>/join -> присоединиться к игре как второй игрок
    # games/<game_id>/move -> сделать ход и обновить состояние игры
    # games/<game_id> -> получить текущее состояние игры

    app.register_blueprint(create_user_blueprint(container)) # чтение публичной информации о пользователе
    # /users/<user_id> -> получить пользователя по UUID
    return app
