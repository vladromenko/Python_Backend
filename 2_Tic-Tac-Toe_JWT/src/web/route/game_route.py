from typing import Any, Dict, Optional  

from flask import Blueprint, jsonify, request, g  

from di.container import Container  
from web.mapper.game_mapper import game_to_dict 


def create_game_blueprint(container: Container) -> Blueprint:  # фабрика blueprint для игрового API
    blueprint = Blueprint("game", __name__)  # создаём blueprint "game"
    auth = container.user_authenticator  # берём компонент, который проверяет авторизацию

    @blueprint.route("/games", methods=["POST"])  # endpoint для создания новой игры
    @auth.protect  # защита: без авторизации нельзя (ставит g.current_user_id)
    def create_game():
        data = request.get_json(silent=True) or {}  # читаем JSON-тело запроса (если нет/битое -> пустой dict)
        vs_computer = _parse_vs_computer(data)  # определяем режим: против компьютера или нет
        try:
            game = container.game_service.create_game(g.current_user_id, vs_computer)  # создаём игру от имени текущего юзера
            return jsonify(game_to_dict(game)), 201  # возвращаем игру в JSON
        except ValueError as exc:  # ошибки в данных/логике
            return jsonify({"error": str(exc)}), 400
        except Exception:  # любые другие ошибки
            return jsonify({"error": "Internal server error."}), 500

    @blueprint.route("/games/available", methods=["GET"])  # endpoint получения доступных текущих игр
    @auth.protect  # нужен залогиненный пользователь
    def list_available_games():
        try:
            games = container.game_service.list_available_games()  # получаем игры из сервиса
            return jsonify({"games": [game_to_dict(game) for game in games]}), 200  # отдаём список игр
        except Exception:
            return jsonify({"error": "Internal server error."}), 500

    @blueprint.route("/games/<game_id>/join", methods=["POST"])  # endpoint присоединиться к игре
    @auth.protect
    def join_game(game_id: str):
        try:
            game = container.game_service.join_game(game_id, g.current_user_id)  # подключаем текущего пользователя к игре
            return jsonify(game_to_dict(game)), 200
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            return jsonify({"error": "Internal server error."}), 500

    @blueprint.route("/games/<game_id>/move", methods=["POST"])  # endpoint обновления текущей игры
    @auth.protect
    def make_move(game_id: str):
        try:
            row, col, board_cells = _parse_move_request(request.get_json(silent=True))  # парсим ход из JSON
            game = container.game_service.make_move(  # передаём ход в сервис
                game_id, g.current_user_id, row, col, board_cells
            )
            return jsonify(game_to_dict(game)), 200  # отдаём обновлённое состояние игры
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            return jsonify({"error": "Internal server error."}), 500

    @blueprint.route("/games/<game_id>", methods=["GET"])  # endpoint получения текущей игры
    @auth.protect
    def get_game(game_id: str):
        try:
            game = container.game_service.get_game(game_id)  # берём игру из сервиса (SELECT из БД)
            return jsonify(game_to_dict(game)), 200
        except ValueError as exc:  # если игры нет
            return jsonify({"error": str(exc)}), 404
        except Exception:
            return jsonify({"error": "Internal server error."}), 500

    @blueprint.route("/games/completed", methods=["GET"])
    @auth.protect
    def list_completed_games():
        try:
            games = container.game_service.list_completed_games(g.current_user_id)
            return jsonify({"games": [game_to_dict(game) for game in games]}), 200
        except Exception:
            return jsonify({"error": "Internal server error."}), 500

    @blueprint.route("/games/leaderboard", methods=["GET"])
    @auth.protect
    def get_leaderboard():
        try:
            top_n = _parse_top_n(request.args.get("n"))
            players = container.game_service.get_top_players(top_n)
            result = []
            for player in players:
                user = container.user_service.get_user(player.user_id)
                if user is None:
                    continue
                result.append(
                    {
                        "user_id": player.user_id,
                        "login": user.login,
                        "win_ratio": player.win_ratio,
                    }
                )
            return jsonify({"players": result}), 200
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            return jsonify({"error": "Internal server error."}), 500

    @blueprint.route("/game/<game_id>", methods=["POST"])  
    @auth.protect
    def play_game(game_id: str):
        try:
            row, col, board_cells = _parse_move_request(request.get_json(silent=True))  # парсим ход
            game = container.game_service.make_move(  # делаем ход 
                game_id, g.current_user_id, row, col, board_cells
            )
            return jsonify(game_to_dict(game)), 200
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            return jsonify({"error": "Internal server error."}), 500

    return blueprint  


def _parse_vs_computer(data: Dict[str, Any]) -> bool:  # вытаскивает флаг "игра против компьютера" из JSON
    if not isinstance(data, dict):  # если пришло не JSON-объект
        return False
    if data.get("opponent") == "computer":  # вариант формата: {"opponent": "computer"}
        return True
    return bool(data.get("vs_computer", False))  # вариант формата: {"vs_computer": true}


def _parse_move_request(  # парсит запрос на ход (координаты или целую доску)
    data: Optional[Dict[str, Any]],
) -> tuple[Optional[int], Optional[int], Optional[list[list[int]]]]:  # возвращает (row, col, cells)
    if not isinstance(data, dict):  # если JSON пустой/битый
        return None, None, None
    row = data.get("row")  # строка хода
    col = data.get("col")  # колонка хода
    if row is not None and col is not None:  # если передали координаты
        return row, col, None
    board_data = data.get("board")  # иначе ожидаем объект board
    if isinstance(board_data, dict):  # board должен быть словарём
        cells = board_data.get("cells")  # достаём "cells"
        if isinstance(cells, list):  # cells должен быть списком списков
            return None, None, cells
    return None, None, None  # если формат не распознан


def _parse_top_n(raw_value: Optional[str]) -> int:
    if raw_value is None:
        raise ValueError("Query parameter n is required.")
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError("n must be a positive integer.") from exc
    if value <= 0:
        raise ValueError("n must be a positive integer.")
    return value
