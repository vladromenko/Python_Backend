from contextlib import contextmanager  

from sqlalchemy import create_engine 
from sqlalchemy.orm import DeclarativeBase, sessionmaker 

# строка подключения к БД:
# postgresql -> используем PostgreSQL
# psycopg2 -> драйвер Python для PostgreSQL
# postgres:postgres -> логин и пароль пользователя БД
# localhost:5432 -> адрес и порт сервера БД
# tictactoe -> имя базы данных
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/tictactoe"

# engine хранит пул подключений и выполняет SQL-команды через SQLAlchemy
# echo=True выводит SQL-запросы в консоль
engine = create_engine(DATABASE_URL, echo=True)

# SessionLocal — фабрика сессий: каждый вызов SessionLocal() создает новую сессию.
SessionLocal = sessionmaker(bind=engine)


# Base — общий базовый класс для всех ORM-моделей
class Base(DeclarativeBase):
    pass 


@contextmanager 
def session_scope():
    with SessionLocal() as session:  # открываем сессию и автоматически закрываем ее в конце блока
        try:
            yield session  # отдаем сессию в код внутри with
            session.commit()  # если ошибок нет, фиксируем изменения в БД
        except Exception:  
            session.rollback()  # откатываем изменения 
            raise  


def init_db() -> None:
    import datasource.model.game 
    import datasource.model.user  

    Base.metadata.create_all(bind=engine)  
