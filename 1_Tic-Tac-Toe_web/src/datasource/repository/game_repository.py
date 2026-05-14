from typing import List, Optional

from sqlalchemy import select

from datasource.db import session_scope
from datasource.mapper.game_mapper import from_domain, to_domain
from datasource.model.game import Game as GameEntity
from domain.model.game import Game
from domain.model.game_state import GameState


class GameRepository:
    def save(self, game: Game) -> Game:
        with session_scope() as session:
            session.merge(from_domain(game))
        return game

    def get(self, game_id: str) -> Optional[Game]:
        with session_scope() as session:
            entity = session.get(GameEntity, game_id)
            if entity is None:
                return None
            return to_domain(entity)

    def list_available(self) -> List[Game]:
        with session_scope() as session:
            stmt = select(GameEntity).where(GameEntity.state == GameState.WAITING.value)
            entities = session.execute(stmt).scalars().all()
            return [to_domain(entity) for entity in entities]
