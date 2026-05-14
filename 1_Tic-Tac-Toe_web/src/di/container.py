from datasource.db import init_db 
from datasource.repository.game_repository import GameRepository
from datasource.repository.user_repository import UserRepository
from domain.service.auth_service_impl import AuthServiceImpl
from domain.service.game_service_impl import GameServiceImpl
from domain.service.user_service_impl import UserServiceImpl
from web.auth.user_authenticator import UserAuthenticator


class Container:  # контейнер создаёт и хранит все нужные объекты приложения
    def __init__(self) -> None:  
        init_db()  # создаём таблицы в PostgreSQL

        self._game_repository = GameRepository()  # репозиторий игр: чтение/запись игр в БД
        self._user_repository = UserRepository()  # репозиторий пользователей: чтение/запись пользователей в БД

        self._user_service = UserServiceImpl(self._user_repository)  # логика пользователей (регистрация, проверка пароля)
        self._user_service.ensure_computer_user()  # гарантируем, что в БД есть служебный пользователь "computer"

        self._auth_service = AuthServiceImpl(self._user_service)  # логика авторизации (signup/login через user_service)
        self._user_authenticator = UserAuthenticator(self._auth_service)  # защита роутов: возвращает 401 если не авторизован

        self._game_service = GameServiceImpl(self._game_repository)  # логика игры (создать игру, присоединиться, ход)

    @property
    def game_service(self) -> GameServiceImpl:
        return self._game_service

    @property
    def auth_service(self) -> AuthServiceImpl:
        return self._auth_service

    @property
    def user_service(self) -> UserServiceImpl:
        return self._user_service

    @property
    def user_authenticator(self) -> UserAuthenticator:
        return self._user_authenticator
