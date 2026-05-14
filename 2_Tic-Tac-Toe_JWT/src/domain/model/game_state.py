from enum import Enum

# состояния для текущей игры
class GameState(str, Enum):
    WAITING = "WAITING"
    PLAYER_TURN = "PLAYER_TURN"
    DRAW = "DRAW"
    WINNER = "WINNER"
