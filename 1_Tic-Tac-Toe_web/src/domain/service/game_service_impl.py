from typing import List, Optional, Tuple
from uuid import uuid4

from datasource.repository.game_repository import GameRepository
from domain.model.board import Board
from domain.model.constants import COMPUTER_USER_ID
from domain.model.game import Game
from domain.model.game_state import GameState
from domain.service.game_service import GameService

EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2
COMPUTER_MARK = PLAYER_O
BOARD_SIZE = 3


class GameServiceImpl(GameService):
    def __init__(self, repository: GameRepository) -> None:
        self._repository = repository

    def create_game(self, creator_id: str, vs_computer: bool) -> Game:  # создать новую игру
        game_id = str(uuid4())  # генерируем уникальный id игры (UUID)
        board = Board(cells=_empty_board())  # создаём пустую доску 3x3

        if vs_computer:  # режим: против компьютера
            player_x_id = creator_id  # создатель играет за X
            player_o_id = COMPUTER_USER_ID  # компьютер играет за O
            current_player_id = player_x_id  # первый ход за X
            state = GameState.PLAYER_TURN  # игра сразу начинается
        else:  # режим: против человека
            player_x_id = creator_id  # создатель играет за X
            player_o_id = None  # второй игрок ещё не подключился
            current_player_id = None  # ход ещё не определён
            state = GameState.WAITING  # ждём второго игрока

        game = Game(  # собираем доменную модель игры
            game_id=game_id,  # id игры
            board=board,  # доска
            state=state,  # состояние
            player_x_id=player_x_id,  # игрок X
            player_o_id=player_o_id,  # игрок O
            current_player_id=current_player_id,  # чей ход
            winner_id=None,  # победителя пока нет
            vs_computer=vs_computer,  # флаг режима
        )

        return self._repository.save(game)  # сохраняем игру в БД и возвращаем

    def list_available_games(self) -> List[Game]:  # список игр, к которым можно присоединиться
        return self._repository.list_available()  # берём из БД (SELECT)


    def join_game(self, game_id: str, user_id: str) -> Game:  # присоединиться к игре
        game = self._repository.get(game_id)  # получить игру из БД по id
        if game is None:  # если нет такой игры
            raise ValueError("Game not found.")
        if game.vs_computer:  # если игра против компьютера — присоединяться нельзя
            raise ValueError("Game is against computer.")
        if game.state != GameState.WAITING or game.player_o_id is not None:  # игра должна ждать второго игрока
            raise ValueError("Game is not available to join.")
        if game.player_x_id == user_id:  # нельзя присоединиться самому к себе второй раз
            raise ValueError("Player is already in the game.")

        updated = Game(  # создаём обновлённое состояние игры
            game_id=game.game_id,  # тот же id
            board=game.board,  # доска пока без изменений
            state=GameState.PLAYER_TURN,  # игра начинается
            player_x_id=game.player_x_id,  # X остаётся прежним
            player_o_id=user_id,  # O = новый игрок
            current_player_id=game.player_x_id,  # первым ходит X
            winner_id=None,  # победителя пока нет
            vs_computer=game.vs_computer,  # режим тот же
        )
        return self._repository.save(updated)  # сохраняем в БД (UPDATE) и возвращаем

   
    def make_move(  # сделать ход
        self,
        game_id: str,  # id игры
        user_id: str,  # кто ходит
        row: Optional[int],  # строка хода 
        col: Optional[int],  # колонка хода
        board_cells: Optional[List[List[int]]],  # или целиком доска (если передают весь board)
    ) -> Game:
        game = self._repository.get(game_id)  # берём игру из БД
        if game is None:  # игры нет
            raise ValueError("Game not found.")
        if game.state == GameState.WAITING:  # второй игрок ещё не подключился
            raise ValueError("Waiting for another player.")
        if game.state in (GameState.DRAW, GameState.WINNER):  # игра уже завершена
            raise ValueError("Game is already finished.")
        if game.current_player_id != user_id:  # проверка очереди хода
            raise ValueError("It is not your turn.")
        if user_id not in (game.player_x_id, game.player_o_id):  # проверка что пользователь участник игры
            raise ValueError("User is not part of this game.")

        expected_mark = _player_mark(game, user_id)  # какая метка у игрока (X или O)
        current_cells = _copy_cells(game.board.cells)  # копируем текущую доску, чтобы не менять оригинал

        move = _resolve_move(current_cells, expected_mark, row, col, board_cells)  # определяем ход (координаты/из доски)
        updated_cells = _apply_move(current_cells, move, expected_mark)  # применяем ход к доске

        if _winner(updated_cells) is not None:  # если после хода есть победитель
            finished = Game(  # собираем финальное состояние игры
                game_id=game.game_id,
                board=Board(cells=updated_cells),
                state=GameState.WINNER,  # алгоритм окончания игры с учетом состояний (выиграл)
                player_x_id=game.player_x_id,
                player_o_id=game.player_o_id,
                current_player_id=None,  # ходов больше нет
                winner_id=user_id,  # победитель = текущий игрок
                vs_computer=game.vs_computer,
            )
            return self._repository.save(finished)  # сохраняем финал в БД

        if _is_draw(updated_cells):  # если ничья
            finished = Game(
                game_id=game.game_id,
                board=Board(cells=updated_cells),
                state=GameState.DRAW, # алгоритм окончания игры с учетом состояний (ничья)
                player_x_id=game.player_x_id,
                player_o_id=game.player_o_id,
                current_player_id=None,
                winner_id=None,  # победителя нет
                vs_computer=game.vs_computer,
            )
            return self._repository.save(finished)  # сохраняем ничью в БД

        if game.vs_computer:  # если игра против компьютера — пусть компьютер сделает следующий ход
            return self._apply_computer_move(game, updated_cells)

        return self._switch_turn(game, updated_cells, user_id)  # иначе просто переключаем ход на другого игрока
        
    def get_game(self, game_id: str) -> Game:
        game = self._repository.get(game_id)
        if game is None:
            raise ValueError("Game not found.")
        return game

    def _apply_computer_move(self, game: Game, cells: List[List[int]]) -> Game:
        move = _find_best_move(cells)
        if move is None:
            finished = Game(
                game_id=game.game_id,
                board=Board(cells=cells),
                state=GameState.DRAW,
                player_x_id=game.player_x_id,
                player_o_id=game.player_o_id,
                current_player_id=None,
                winner_id=None,
                vs_computer=game.vs_computer,
            )
            return self._repository.save(finished)

        updated_cells = _apply_move(cells, move, COMPUTER_MARK)
        if _winner(updated_cells) == COMPUTER_MARK:
            finished = Game(
                game_id=game.game_id,
                board=Board(cells=updated_cells),
                state=GameState.WINNER,
                player_x_id=game.player_x_id,
                player_o_id=game.player_o_id,
                current_player_id=None,
                winner_id=COMPUTER_USER_ID,
                vs_computer=game.vs_computer,
            )
            return self._repository.save(finished)
        if _is_draw(updated_cells):
            finished = Game(
                game_id=game.game_id,
                board=Board(cells=updated_cells),
                state=GameState.DRAW,
                player_x_id=game.player_x_id,
                player_o_id=game.player_o_id,
                current_player_id=None,
                winner_id=None,
                vs_computer=game.vs_computer,
            )
            return self._repository.save(finished)

        next_turn = Game(
            game_id=game.game_id,
            board=Board(cells=updated_cells),
            state=GameState.PLAYER_TURN,
            player_x_id=game.player_x_id,
            player_o_id=game.player_o_id,
            current_player_id=game.player_x_id,
            winner_id=None,
            vs_computer=game.vs_computer,
        )
        return self._repository.save(next_turn)

    def _switch_turn(
        self, game: Game, updated_cells: List[List[int]], user_id: str
    ) -> Game:
        next_player = _other_player_id(game, user_id)
        updated = Game(
            game_id=game.game_id,
            board=Board(cells=updated_cells),
            state=GameState.PLAYER_TURN,
            player_x_id=game.player_x_id,
            player_o_id=game.player_o_id,
            current_player_id=next_player,
            winner_id=None,
            vs_computer=game.vs_computer,
        )
        return self._repository.save(updated)


def _resolve_move(
    current_cells: List[List[int]],
    expected_mark: int,
    row: Optional[int],
    col: Optional[int],
    board_cells: Optional[List[List[int]]],
) -> Tuple[int, int]:
    if row is not None and col is not None:
        _validate_move_coords(row, col)
        if current_cells[row][col] != EMPTY:
            raise ValueError("Cell is already occupied.")
        return row, col
    if board_cells is None:
        raise ValueError("Move coordinates or board must be provided.")
    _validate_shape(board_cells)
    _validate_values(board_cells)
    return _extract_move(current_cells, board_cells, expected_mark)


def _extract_move(
    prev_cells: List[List[int]],
    new_cells: List[List[int]],
    expected_value: int,
) -> Tuple[int, int]:
    move = None
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            prev = prev_cells[row][col]
            new = new_cells[row][col]
            if prev == new:
                continue
            if prev != EMPTY:
                raise ValueError("Previous moves cannot be changed.")
            if new != expected_value:
                raise ValueError("Move value does not match player mark.")
            if move is not None:
                raise ValueError("Only one move is allowed per turn.")
            move = (row, col)
    if move is None:
        raise ValueError("No new move found.")
    return move


def _player_mark(game: Game, user_id: str) -> int:
    if user_id == game.player_x_id:
        return PLAYER_X
    if user_id == game.player_o_id:
        return PLAYER_O
    raise ValueError("User is not part of this game.")


def _other_player_id(game: Game, user_id: str) -> str:
    other = game.player_o_id if user_id == game.player_x_id else game.player_x_id
    if other is None:
        raise ValueError("Second player is missing.")
    return other


def _find_best_move(cells: List[List[int]]) -> Optional[Tuple[int, int]]:
    best_score, move = _minimax(cells, COMPUTER_MARK)
    return move


def _minimax(
    cells: List[List[int]], player: int
) -> Tuple[int, Optional[Tuple[int, int]]]:
    winner = _winner(cells)
    if winner == COMPUTER_MARK:
        return 10, None
    if winner == PLAYER_X:
        return -10, None
    if _is_draw(cells):
        return 0, None
    best_score = None
    best_move = None
    for move in _available_moves(cells):
        next_cells = _apply_move(cells, move, player)
        score, _ = _minimax(next_cells, _other_mark(player))
        best_score, best_move = _choose_score(
            player, score, move, best_score, best_move
        )
    return best_score, best_move


def _choose_score(
    player: int,
    score: int,
    move: Tuple[int, int],
    best_score: Optional[int],
    best_move: Optional[Tuple[int, int]],
) -> Tuple[int, Tuple[int, int]]:
    if best_score is None:
        return score, move
    if player == COMPUTER_MARK and score > best_score:
        return score, move
    if player != COMPUTER_MARK and score < best_score:
        return score, move
    return best_score, best_move


def _available_moves(cells: List[List[int]]) -> List[Tuple[int, int]]:
    return [
        (row, col)
        for row in range(BOARD_SIZE)
        for col in range(BOARD_SIZE)
        if cells[row][col] == EMPTY
    ]


def _apply_move(
    cells: List[List[int]], move: Tuple[int, int], player: int
) -> List[List[int]]:
    row, col = move
    new_cells = _copy_cells(cells)
    new_cells[row][col] = player
    return new_cells


def _winner(cells: List[List[int]]) -> Optional[int]:
    for line in _lines(cells):
        if line[0] != EMPTY and line[0] == line[1] == line[2]:
            return line[0]
    return None


def _lines(cells: List[List[int]]) -> List[List[int]]:
    rows = [row[:] for row in cells]
    cols = [
        [cells[row_index][col_index] for row_index in range(BOARD_SIZE)]
        for col_index in range(BOARD_SIZE)
    ]
    diags = [
        [cells[i][i] for i in range(BOARD_SIZE)],
        [cells[i][BOARD_SIZE - 1 - i] for i in range(BOARD_SIZE)],
    ]
    return rows + cols + diags


def _is_draw(cells: List[List[int]]) -> bool:
    if _winner(cells) is not None:
        return False
    return all(value != EMPTY for row in cells for value in row)


def _other_mark(player: int) -> int:
    return PLAYER_X if player == COMPUTER_MARK else COMPUTER_MARK


def _validate_shape(cells: List[List[int]]) -> None:
    if not isinstance(cells, list) or len(cells) != BOARD_SIZE:
        raise ValueError("Board must be a 3x3 matrix.")
    for row in cells:
        if not isinstance(row, list) or len(row) != BOARD_SIZE:
            raise ValueError("Board must be a 3x3 matrix.")


def _validate_values(cells: List[List[int]]) -> None:
    for row in cells:
        for value in row:
            if value not in (EMPTY, PLAYER_X, PLAYER_O):
                raise ValueError("Board contains invalid values.")


def _validate_move_coords(row: int, col: int) -> None:
    if not isinstance(row, int) or not isinstance(col, int):
        raise ValueError("Move coordinates must be integers.")
    if row < 0 or row >= BOARD_SIZE or col < 0 or col >= BOARD_SIZE:
        raise ValueError("Move coordinates are out of bounds.")


def _copy_cells(cells: List[List[int]]) -> List[List[int]]:
    return [row[:] for row in cells]


def _empty_board() -> List[List[int]]:
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
