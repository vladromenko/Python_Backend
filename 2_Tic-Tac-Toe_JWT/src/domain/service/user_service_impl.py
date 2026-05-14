from typing import Optional 
from uuid import uuid4  # генерация UUID 

from werkzeug.security import check_password_hash, generate_password_hash 

from datasource.repository.user_repository import UserRepository  
from domain.model.constants import COMPUTER_LOGIN, COMPUTER_PASSWORD, COMPUTER_USER_ID  
from domain.model.sign_up_request import SignUpRequest 
from domain.model.user import User  
from domain.service.user_service import UserService  

# поддержка пользователя в слое domain 
class UserServiceImpl(UserService):  # реализация сервиса пользователей (логика поверх репозитория)
    def __init__(self, repository: UserRepository) -> None:  # конструктор: получаем репозиторий через DI
        self._repository = repository  # сохраняем репозиторий для работы с БД

    def create_user(self, request: SignUpRequest) -> User:  # регистрация нового пользователя
        _validate_login_password(request.login, request.password)  # проверка, что логин/пароль норм
        if request.login == COMPUTER_LOGIN:  # запрет зарезервированного логина
            raise ValueError("Login is reserved.")
        existing = self._repository.get_by_login(request.login)  # запрос в БД: есть ли уже такой логин
        if existing is not None:  # если найден — регистрация запрещена
            raise ValueError("Login already exists.")
        user = User(  # создаём пользователя
            user_id=str(uuid4()),  # генерируем новый уникальный user_id
            login=request.login,  # сохраняем логин
            password_hash=generate_password_hash(request.password),  # хэшируем пароль перед сохранением
        )
        return self._repository.save(user)  # сохраняем пользователя в БД (INSERT/UPDATE) и возвращаем доменный объект

    def get_user(self, user_id: str) -> Optional[User]:  # получить пользователя по id
        return self._repository.get_by_id(user_id)  # запрос в БД: SELECT по primary key

    def get_by_login(self, login: str) -> Optional[User]:  # получить пользователя по логину
        return self._repository.get_by_login(login)  # запрос в БД: SELECT WHERE login=...

    def validate_credentials(self, login: str, password: str) -> Optional[User]:  # проверка логина/пароля (авторизация)
        user = self._repository.get_by_login(login)  # запрос в БД: найти пользователя по логину
        if user is None:  # если такого логина нет
            return None
        if not check_password_hash(user.password_hash, password):  # сравнение пароля с хэшем
            return None
        return user  # вернём пользователя, если пароль верный

    def ensure_computer_user(self) -> None:  # гарантирует наличие служебного "компьютерного" пользователя
        existing = self._repository.get_by_login(COMPUTER_LOGIN)  # запрос в БД: есть ли "computer"
        if existing is not None:  # если уже есть — ничего не делаем
            return
        user = User(  # создаём служебного пользователя
            user_id=COMPUTER_USER_ID,  # фиксированный id из констант
            login=COMPUTER_LOGIN,  # фиксированный логин из констант
            password_hash=generate_password_hash(COMPUTER_PASSWORD),  # хэшируем фиксированный пароль
        )
        self._repository.save(user)  # сохраняем в БД (INSERT)


def _validate_login_password(login: str, password: str) -> None:  # простая валидация входных данных
    if not login or not isinstance(login, str):  # логин обязателен и должен быть строкой
        raise ValueError("Login is required.")
    if not password or not isinstance(password, str):  # пароль обязателен и должен быть строкой
        raise ValueError("Password is required.")