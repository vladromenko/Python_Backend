from dataclasses import dataclass
from typing import Optional

from domain.model.board import Board
from domain.model.game_state import GameState


@dataclass(frozen=True)
class Game:
    game_id: str
    board: Board
    state: GameState
    player_x_id: Optional[str] # информация о значках игроков
    player_o_id: Optional[str] # информация о значках игроков
    current_player_id: Optional[str] # поле UUID текущего хода 
    winner_id: Optional[str] # поле UUID победителя 
    vs_computer: bool
