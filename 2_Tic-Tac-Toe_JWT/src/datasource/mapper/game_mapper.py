from typing import List  

from datasource.model.game import Game as DataGame  
from domain.model.board import Board as DomainBoard 
from domain.model.game import Game as DomainGame 
from domain.model.game_state import GameState


def to_domain(data_game: DataGame) -> DomainGame:  # перевод из модели БД в доменную модель
    return DomainGame(
        game_id=data_game.game_id,  # id игры
        created_at=data_game.created_at,
        board=DomainBoard(cells=_copy_cells(data_game.board)),  # доска (копия матрицы)
        state=GameState(data_game.state),  # строку состояния -> enum
        player_x_id=data_game.player_x_id,  # игрок X
        player_o_id=data_game.player_o_id,  # игрок O
        current_player_id=data_game.current_player_id,  # чей ход
        winner_id=data_game.winner_id,  # победитель
        vs_computer=data_game.vs_computer,  # игра с компьютером
    )


def from_domain(domain_game: DomainGame) -> DataGame:  # перевод из доменной модели в модель БД
    return DataGame(
        game_id=domain_game.game_id,  # id игры
        created_at=domain_game.created_at,
        board=_copy_cells(domain_game.board.cells),  # доска -> JSON (копия матрицы)
        state=domain_game.state.value,  # enum -> строка для БД
        player_x_id=domain_game.player_x_id,  # игрок X
        player_o_id=domain_game.player_o_id,  # игрок O
        current_player_id=domain_game.current_player_id,  # чей ход
        winner_id=domain_game.winner_id,  # победитель
        vs_computer=domain_game.vs_computer,  # игра с компьютером
    )


def _copy_cells(cells: List[List[int]]) -> List[List[int]]:  # глубокая копия матрицы 2D
    return [row[:] for row in cells]  # копируем каждую строку отдельно
