1) Создать и активировать виртуальное окружение (если его нет)

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install flask sqlalchemy psycopg2-binary

2) Убедиться, что PostgreSQL запущен и база существует

export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"
pg_isready -h localhost -p 5432
createdb tictactoe

3) Запустить сервер

export DATABASE_URL="postgresql+psycopg2://$USER@localhost:5432/tictactoe"
python3 app.py

Все эндпоинты

### Авторизация

Регистрация

curl -X POST http://localhost:5001/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"login":"user1","password":"pass1"}'

Логин (Basic Auth)

curl -u user1:pass1 -X POST http://localhost:5001/auth/login

### Игры

Создать игру с компьютером

curl -u user1:pass1 -X POST http://localhost:5001/games \
  -H "Content-Type: application/json" \
  -d '{"vs_computer": true}'

Создать игру с человеком

curl -u user1:pass1 -X POST http://localhost:5001/games \
  -H "Content-Type: application/json" \
  -d '{}'

Список доступных игр

curl -u user1:pass1 http://localhost:5001/games/available


Присоединиться к игре

curl -u user2:pass2 -X POST http://localhost:5001/games/GAME_ID/join

Сделать ход

curl -u user1:pass1 -X POST http://localhost:5001/games/GAME_ID/move \
  -H "Content-Type: application/json" \
  -d '{"row":0,"col":2}'

Получить состояние игры

curl -u user1:pass1 http://localhost:5001/games/GAME_ID


Старый совместимый эндпоинт

curl -u user1:pass1 -X POST http://localhost:5001/game/GAME_ID \
  -H "Content-Type: application/json" \
  -d '{"row":0,"col":2}'


### Пользователи

Получить пользователя по UUID

curl -u user1:pass1 http://localhost:5001/users/USER_ID

## Игра человек против человека (пошагово)

1) Регистрация двух игроков

curl -X POST http://localhost:5001/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"login":"user1","password":"pass1"}'

curl -X POST http://localhost:5001/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"login":"user2","password":"pass2"}'

2) Игрок 1 создаёт игру

curl -u user1:pass1 -X POST http://localhost:5001/games \
  -H "Content-Type: application/json" \
  -d '{}'

3) Игрок 2 присоединяется

curl -u user2:pass2 -X POST http://localhost:5001/games/GAME_ID/join

4) Ходы по очереди

curl -u user1:pass1 -X POST http://localhost:5001/games/GAME_ID/move \
  -H "Content-Type: application/json" \
  -d '{"row":0,"col":0}'

5) Проверка состояния и очереди

curl -u user1:pass1 http://localhost:5001/games/GAME_ID

Смотри `current_player_id`, ход делает тот, чей UUID там указан.

## Игра человек против компьютера (пошагово)

1) Регистрация

curl -X POST http://localhost:5001/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"login":"user1","password":"pass1"}'

2) Создание игры с компьютером

curl -u user1:pass1 -X POST http://localhost:5001/games \
  -H "Content-Type: application/json" \
  -d '{"vs_computer": true}'

3) Делать ходы

curl -u user1:pass1 -X POST http://localhost:5001/games/GAME_ID/move \
  -H "Content-Type: application/json" \
  -d '{"row":1,"col":1}'

4) Проверять состояние

curl -u user1:pass1 http://localhost:5001/games/GAME_ID

Компьютер ходит автоматически после твоего хода.

## Как удалить все игры

psql "postgresql://$USER@localhost:5432/tictactoe" -c "DELETE FROM games;"
