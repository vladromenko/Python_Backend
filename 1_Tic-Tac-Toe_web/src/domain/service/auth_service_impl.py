import base64

from domain.model.sign_up_request import SignUpRequest
from domain.service.auth_service import AuthError, AuthService
from domain.service.user_service import UserService

# сервис авторизации, который использует UserService
class AuthServiceImpl(AuthService):  # сервис авторизации/регистрации (реализация интерфейса AuthService)
    def __init__(self, user_service: UserService) -> None:  # конструктор: получаем сервис пользователей
        self._user_service = user_service  # сохраняем ссылку на user_service (через него будет работа с БД)

    # метод регистрации - принимает SignUpRequest и возвращает факт успешной регистрации
    def register(self, request: SignUpRequest) -> bool:  # регистрация пользователя
        self._user_service.create_user(request)  # создаём пользователя (внутри: проверки + запись в БД)
        return True  # сигнал успеха

    # метод авторизации - принимает base 64 и возвращает uuid
    def authorize(self, authorization_header: str) -> str:  # авторизация по заголовку Authorization
        login, password = _decode_basic_auth(authorization_header)  # достаём логин/пароль из Basic Auth
        user = self._user_service.validate_credentials(login, password)  # проверяем: есть ли пользователь + совпадает ли пароль
        if user is None:  # если не найден или пароль неверный
            raise AuthError("Invalid login or password.")  # ошибка авторизации
        return user.user_id  # успех: возвращаем id пользователя


def _decode_basic_auth(authorization_header: str) -> tuple[str, str]:  # парсинг Basic Auth -> (login, password)
    if not authorization_header:  # заголовок пустой/нет
        raise AuthError("Missing authorization header.")
    header = authorization_header.strip()  # убираем пробелы по краям
    if header.lower().startswith("basic "):  # если заголовок в виде Basic <base64>
        encoded = header[6:].strip()  # отрезаем "Basic " (6 символов) и берём только base64 часть
    else:
        encoded = header  # если пришла просто base64-строка без префикса

    try:
        decoded = base64.b64decode(encoded).decode("utf-8")  # base64 -> bytes -> строка вида "login:password"
    except Exception as exc:  # если base64 битый или не декодируется
        raise AuthError("Invalid authorization encoding.") from exc

    if ":" not in decoded:  # формат должен быть "login:password"
        raise AuthError("Invalid authorization format.")

    login, password = decoded.split(":", 1)  # делим по первому двоеточию (пароль может содержать ':' дальше)
    if not login or not password:  # оба значения обязательны
        raise AuthError("Login and password are required.")
    return login, password  # возвращаем пару для дальнейшей проверки