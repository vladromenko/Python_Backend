from dataclasses import dataclass
from typing import Optional

from web.model.board import Board


@dataclass(frozen=True)
class Game:
    game_id: str
    board: Board
    state: str
    player_x_id: Optional[str]
    player_o_id: Optional[str]
    current_player_id: Optional[str]
    winner_id: Optional[str]
    vs_computer: bool
