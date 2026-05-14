from typing import Any, Dict, List

from domain.model.game import Game


def game_to_dict(game: Game) -> Dict[str, Any]:
    return {
        "game_id": game.game_id,
        "created_at": game.created_at.isoformat(),
        "state": game.state.value,
        "board": {"cells": _copy_cells(game.board.cells)},
        "player_x_id": game.player_x_id,
        "player_o_id": game.player_o_id,
        "current_player_id": game.current_player_id,
        "winner_id": game.winner_id,
        "vs_computer": game.vs_computer,
        "symbols": {"X": game.player_x_id, "O": game.player_o_id},
    }


def _copy_cells(cells: List[List[int]]) -> List[List[int]]:
    return [row[:] for row in cells]
