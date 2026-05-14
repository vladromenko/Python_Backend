from dataclasses import dataclass

# модель для UUID пользователя и соотношения побед
@dataclass(frozen=True)
class PlayerWinRatio:
    user_id: str
    win_ratio: float
