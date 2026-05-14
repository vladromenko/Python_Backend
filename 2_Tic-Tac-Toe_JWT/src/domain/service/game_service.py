from abc import ABC, abstractmethod
from typing import List, Optional

from domain.model.game import Game
from domain.model.player_win_ratio import PlayerWinRatio


class GameService(ABC):
    @abstractmethod
    def create_game(self, creator_id: str, vs_computer: bool) -> Game:
        raise NotImplementedError

    @abstractmethod
    def list_available_games(self) -> List[Game]:
        raise NotImplementedError

    @abstractmethod
    def join_game(self, game_id: str, user_id: str) -> Game:
        raise NotImplementedError

    @abstractmethod
    def make_move(
        self,
        game_id: str,
        user_id: str,
        row: Optional[int],
        col: Optional[int],
        board_cells: Optional[List[List[int]]],
    ) -> Game:
        raise NotImplementedError

    @abstractmethod
    def get_game(self, game_id: str) -> Game:
        raise NotImplementedError

    @abstractmethod
    def list_completed_games(self, user_id: str) -> List[Game]:
        raise NotImplementedError

    @abstractmethod
    def get_top_players(self, limit: int) -> List[PlayerWinRatio]:
        raise NotImplementedError
