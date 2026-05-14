from typing import Optional  

from sqlalchemy import select 

from datasource.db import session_scope 
from datasource.model.user import User as UserEntity  
from domain.model.user import User 

# поддержка пользователя в слое datasource
class UserRepository:
    def save(self, user: User) -> User:  # сохранить пользователя (вставка/обновление)
        with session_scope() as session:  # открыть сессию БД (транзакция)
            session.merge(  
                UserEntity(  # создаём ORM-объект для таблицы users
                    user_id=user.user_id,  # id пользователя
                    login=user.login,  # логин
                    password_hash=user.password_hash,  # хэш пароля
                )
            )
        return user 

    def get_by_id(self, user_id: str) -> Optional[User]:  # получить пользователя по id
        with session_scope() as session:  # открыть сессию БД
            entity = session.get(UserEntity, user_id)  # SELECT по primary key
            if entity is None:  # если не найдено
                return None
            return User(  # преобразуем ORM-объект в доменную модель
                user_id=entity.user_id,
                login=entity.login,
                password_hash=entity.password_hash,
            )

    def get_by_login(self, login: str) -> Optional[User]:  # получить пользователя по логину
        with session_scope() as session:  # открыть сессию БД
            stmt = select(UserEntity).where(UserEntity.login == login)  # SELECT ... WHERE login = :login
            entity = session.execute(stmt).scalars().first()  # выполнить запрос и взять первую запись
            if entity is None:  # если не найдено
                return None
            return User(  # преобразуем ORM-объект в доменную модель
                user_id=entity.user_id,
                login=entity.login,
                password_hash=entity.password_hash,
            )