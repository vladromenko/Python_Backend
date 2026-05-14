from sqlalchemy import String  

from sqlalchemy.orm import Mapped, mapped_column 

from datasource.db import Base 

# поддержка пользователя в слое datasource
class User(Base):  # объявляем ORM-модель: этот класс будет соответствовать таблице в PostgreSQL
    __tablename__ = "users"  # имя таблицы в базе данных будет "users"

    user_id: Mapped[str] = mapped_column(  # колонка user_id; в Python это str, в БД это строка (VARCHAR)
        String(36),  # ограничение длины: максимум 36 символов (часто так хранят UUID в виде строки)
        primary_key=True,  # первичный ключ: уникальный идентификатор записи (строки) в таблице users
    )

    login: Mapped[str] = mapped_column(  # колонка login; хранит логин пользователя
        String(64),  # максимум 64 символа
        unique=True,  # уникальность: в таблице users не может быть двух одинаковых login
        nullable=False,  # нельзя NULL: логин обязан быть задан
    )

    password_hash: Mapped[str] = mapped_column(  # колонка password_hash; хранит НЕ пароль, а его хэш
        String(255),  # максимум 255 символов (обычно хватает для bcrypt/argon2/прочих форматов)
        nullable=False,  # нельзя NULL: у пользователя всегда должен быть сохранён хэш пароля
    )