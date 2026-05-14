from typing import List, Optional

from sqlalchemy import Float, and_, case, cast, desc, func, or_, select, union_all

from datasource.db import session_scope
from datasource.mapper.game_mapper import from_domain, to_domain
from datasource.model.game import Game as GameEntity
from domain.model.constants import COMPUTER_USER_ID
from domain.model.game import Game
from domain.model.game_state import GameState
from domain.model.player_win_ratio import PlayerWinRatio


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

    def list_completed_by_user(self, user_id: str) -> List[Game]:
        with session_scope() as session:
            stmt = (
                select(GameEntity)
                .where(
                    or_(
                        and_(
                            GameEntity.state == GameState.WINNER.value,
                            GameEntity.winner_id == user_id,
                        ),
                        and_(
                            GameEntity.state == GameState.DRAW.value,
                            or_(
                                GameEntity.player_x_id == user_id,
                                GameEntity.player_o_id == user_id,
                            ),
                        ),
                    )
                )
                .order_by(desc(GameEntity.created_at)) # сначала новые игры
            )
            entities = session.execute(stmt).scalars().all()  # выполнить запрос; вернуть список GameEntity 
            return [to_domain(entity) for entity in entities] 
    # запрос для расчета соотношения побед, сортировки и выбора
    def get_top_players(self, limit: int) -> List[PlayerWinRatio]:
        with session_scope() as session:
            completed_states = [GameState.WINNER.value, GameState.DRAW.value] # какие состояния считаем завершёнными

            participants_x = select(
                GameEntity.player_x_id.label("user_id"),
                GameEntity.state.label("state"),
                GameEntity.winner_id.label("winner_id"),
            ).where(
                GameEntity.player_x_id.is_not(None),
                GameEntity.state.in_(completed_states),
            )

            participants_o = select(
                GameEntity.player_o_id.label("user_id"),
                GameEntity.state.label("state"),
                GameEntity.winner_id.label("winner_id"),
            ).where(
                GameEntity.player_o_id.is_not(None),
                GameEntity.state.in_(completed_states),
            )

            participants = union_all(participants_x, participants_o).subquery() # склеить в одну таблицу-выборку participants(user_id,state,winner_id)

            wins = func.sum( # посчитать количество побед внутри группы (на одного user_id)
                case(
                    (
                        and_(
                            participants.c.state == GameState.WINNER.value,
                            participants.c.winner_id == participants.c.user_id,
                        ),
                        1,
                    ),
                    else_=0,
                )
            )

            losses_and_draws = func.sum( # посчитать количество (поражения + ничьи) внутри группы
                case(
                    (
                        or_(
                            participants.c.state == GameState.DRAW.value,
                            and_(
                                participants.c.state == GameState.WINNER.value,
                                participants.c.winner_id != participants.c.user_id,
                            ),
                        ),
                        1,
                    ),
                    else_=0,
                )
            )

            ratio = case( # вычисляем win_ratio на игрока: wins/(losses+draws)
                (losses_and_draws == 0, cast(wins, Float)), # если (losses+draws)=0 -> win_ratio = wins (float)
                else_=cast(wins, Float) / cast(losses_and_draws, Float), # иначе win_ratio = wins/(losses+draws) (float)
            ).label("win_ratio")

            stmt = ( # финальный SELECT, который реально пойдёт в БД
                select(participants.c.user_id.label("user_id"), ratio) 
                .where(participants.c.user_id != COMPUTER_USER_ID)
                .group_by(participants.c.user_id)
                .order_by(desc(ratio), participants.c.user_id)
                .limit(limit)
            )

            rows = session.execute(stmt).all() # выполнить запрос; вернуть список строк (user_id, win_ratio)
            return [  # превратить строки из БД в список доменных объектов PlayerWinRatio
                PlayerWinRatio(
                    user_id=row.user_id,
                    win_ratio=float(row.win_ratio or 0.0),
                )
                for row in rows
            ]
