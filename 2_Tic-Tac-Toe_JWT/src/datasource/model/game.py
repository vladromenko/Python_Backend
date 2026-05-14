from typing import List, Optional 

from datetime import datetime

from sqlalchemy import Boolean, DateTime, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column 

from datasource.db import Base  # Base — базовый класс SQLAlchemy, от него наследуются все модели (таблицы)


class Game(Base):  # ORM-модель: этот класс будет связан с таблицей в PostgreSQL
    __tablename__ = "games"  # имя таблицы в базе данных (будет таблица games)

    game_id: Mapped[str] = mapped_column(  # колонка game_id, в Python это str, в БД это строка
        String(36),  # SQL-тип: строка до 36 символов (часто так хранят UUID)
        primary_key=True,  # первичный ключ: уникальный идентификатор строки/игры
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    board: Mapped[List[List[int]]] = mapped_column(  # колонка board: в Python это "матрица чисел"
        JSON,  # SQL-тип JSON: хранит структуру вроде [[0,1,0],[2,0,0],[0,0,0]]
        nullable=False,  # нельзя хранить NULL: доска обязана быть
    )

    state: Mapped[str] = mapped_column(  # колонка state: строка, например "IN_PROGRESS"
        String(32),  # до 32 символов
        nullable=False,  # состояние обязательно
    )

    player_x_id: Mapped[Optional[str]] = mapped_column(  # id игрока за X: может быть строка или None
        String(36),  # строка до 36 символов
        nullable=True,  # можно NULL: например, пока игрок не присоединился
    )

    player_o_id: Mapped[Optional[str]] = mapped_column(  # id игрока за O: может быть строка или None
        String(36),  # строка до 36 символов
        nullable=True,  # можно NULL
    )

    current_player_id: Mapped[Optional[str]] = mapped_column(  # чей сейчас ход: id игрока или None
        String(36),  # строка до 36 символов
        nullable=True,  # можно NULL (например, игра ещё не стартовала)
    )

    winner_id: Mapped[Optional[str]] = mapped_column(  # победитель: id игрока или None
        String(36),  # строка до 36 символов
        nullable=True,  # можно NULL, если победителя ещё нет или ничья
    )

    vs_computer: Mapped[bool] = mapped_column(  # игра против компьютера: True/False
        Boolean,  # SQL-тип булево
        nullable=False,  # нельзя NULL, значение всегда должно быть
        default=False,  # значение по умолчанию: False (если не указали — игра не против компьютера)
    )
