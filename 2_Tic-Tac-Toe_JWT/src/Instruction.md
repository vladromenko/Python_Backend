1) Создать и активировать виртуальное окружение (если его нет)

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install flask sqlalchemy psycopg2-binary flask-jwt-extended

Изменилось: добавилась зависимость `flask-jwt-extended` для JWT-авторизации.

2) Убедиться, что PostgreSQL запущен и база существует

export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"
pg_isready -h localhost -p 5432
PGPASSWORD=postgres createdb -U postgres -h localhost -p 5432 tictactoe

Если база уже существует и нужно удалить её полностью

PGPASSWORD=postgres dropdb -U postgres -h localhost -p 5432 tictactoe

Если PostgreSQL пишет, что база используется, сначала завершить подключения

PGPASSWORD=postgres psql -U postgres -h localhost -p 5432 -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'tictactoe' AND pid <> pg_backend_pid();"

Потом создать заново

PGPASSWORD=postgres createdb -U postgres -h localhost -p 5432 tictactoe

3) Запустить сервер

cd src
python3 app.py

Все эндпоинты

### Авторизация

Регистрация

curl -X POST http://localhost:5001/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"login":"user1","password":"pass1"}'

Логин

TOKENS=$(curl -s -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"user1","password":"pass1"}')

echo "$TOKENS"

ACCESS_TOKEN=$(printf '%s' "$TOKENS" | python3 -c 'import sys, json; print(json.load(sys.stdin)["accessToken"])')
REFRESH_TOKEN=$(printf '%s' "$TOKENS" | python3 -c 'import sys, json; print(json.load(sys.stdin)["refreshToken"])')

Посмотреть сохранённые токены

echo "$ACCESS_TOKEN"
echo "$REFRESH_TOKEN"

Изменилось: раньше был `Basic Auth`, теперь логин идет JSON-телом и возвращает `accessToken` и `refreshToken`.

Токены сохраняются в переменные shell `$ACCESS_TOKEN` и `$REFRESH_TOKEN`.

Пример ответа в `TOKENS`

{
  "type": "Bearer",
  "accessToken": "ACCESS_TOKEN",
  "refreshToken": "REFRESH_TOKEN"
}

Обновить access token

curl -X POST http://localhost:5001/auth/access-token \
  -H "Content-Type: application/json" \
  -d "{\"refreshToken\":\"$REFRESH_TOKEN\"}"

Обновить refresh token

curl -X POST http://localhost:5001/auth/refresh-token \
  -H "Content-Type: application/json" \
  -d "{\"refreshToken\":\"$REFRESH_TOKEN\"}"

Получить текущего пользователя по access token

curl http://localhost:5001/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"

### Игры

Создать игру с компьютером

curl -X POST http://localhost:5001/games \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"vs_computer": true}'

Создать игру с человеком

curl -X POST http://localhost:5001/games \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

Список доступных игр

curl http://localhost:5001/games/available \
  -H "Authorization: Bearer $ACCESS_TOKEN"

Важно: здесь показываются только игры со статусом `WAITING`, то есть ожидающие второго игрока. Игры против компьютера в этот список не попадают.

Присоединиться к игре вторым игроком

curl -X POST http://localhost:5001/games/GAME_ID/join \
  -H "Authorization: Bearer $ACCESS_TOKEN_2"

Важно: создатель игры не может присоединиться к ней же ещё раз. Для `join` нужен токен другого пользователя.

Сделать ход

curl -X POST http://localhost:5001/games/GAME_ID/move \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"row":0,"col":2}'

Получить состояние игры

curl http://localhost:5001/games/GAME_ID \
  -H "Authorization: Bearer $ACCESS_TOKEN"

История завершенных игр

curl http://localhost:5001/games/completed \
  -H "Authorization: Bearer $ACCESS_TOKEN"

Таблица лидеров

curl "http://localhost:5001/games/leaderboard?n=5" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

Изменилось: все игровые endpoint теперь работают через `Bearer accessToken`; в ответе игры добавилось поле `created_at`.

Старый совместимый эндпоинт

curl -X POST http://localhost:5001/game/GAME_ID \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"row":0,"col":2}'

### Пользователи

Получить пользователя по UUID

curl http://localhost:5001/users/USER_ID \
  -H "Authorization: Bearer $ACCESS_TOKEN"

Получить текущего пользователя

curl http://localhost:5001/users/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"

Изменилось: добавлен endpoint `/users/me`.

## Игра человек против человека (пошагово)

1) Регистрация двух игроков

curl -X POST http://localhost:5001/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"login":"user1","password":"pass1"}'

curl -X POST http://localhost:5001/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"login":"user2","password":"pass2"}'

2) Игрок 1 логинится и получает `ACCESS_TOKEN_1`

TOKENS_1=$(curl -s -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"user1","password":"pass1"}')

ACCESS_TOKEN_1=$(printf '%s' "$TOKENS_1" | python3 -c 'import sys, json; print(json.load(sys.stdin)["accessToken"])')

3) Игрок 2 логинится и получает `ACCESS_TOKEN_2`

TOKENS_2=$(curl -s -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"user2","password":"pass2"}')

ACCESS_TOKEN_2=$(printf '%s' "$TOKENS_2" | python3 -c 'import sys, json; print(json.load(sys.stdin)["accessToken"])')

4) Игрок 1 создаёт игру

curl -X POST http://localhost:5001/games \
  -H "Authorization: Bearer $ACCESS_TOKEN_1" \
  -H "Content-Type: application/json" \
  -d '{}'

5) Игрок 2 присоединяется

curl -X POST http://localhost:5001/games/GAME_ID/join \
  -H "Authorization: Bearer $ACCESS_TOKEN_2"

6) Ходы по очереди

curl -X POST http://localhost:5001/games/GAME_ID/move \
  -H "Authorization: Bearer $ACCESS_TOKEN_1" \
  -H "Content-Type: application/json" \
  -d '{"row":0,"col":0}'

7) Проверка состояния и очереди

curl http://localhost:5001/games/GAME_ID \
  -H "Authorization: Bearer $ACCESS_TOKEN_1"

## Игра человек против компьютера (пошагово)

1) Регистрация

curl -X POST http://localhost:5001/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"login":"user1","password":"pass1"}'

2) Логин и получение `ACCESS_TOKEN`

TOKENS=$(curl -s -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"user1","password":"pass1"}')

ACCESS_TOKEN=$(printf '%s' "$TOKENS" | python3 -c 'import sys, json; print(json.load(sys.stdin)["accessToken"])')

3) Создание игры с компьютером

curl -X POST http://localhost:5001/games \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"vs_computer": true}'

4) Делать ходы

curl -X POST http://localhost:5001/games/GAME_ID/move \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"row":1,"col":1}'

5) Проверять состояние

curl http://localhost:5001/games/GAME_ID \
  -H "Authorization: Bearer $ACCESS_TOKEN"

Компьютер ходит автоматически после твоего хода.

## Как удалить все игры

psql "postgresql://postgres:postgres@localhost:5432/tictactoe" -c "DELETE FROM games;"
psql "postgresql://postgres:postgres@localhost:5432/tictactoe" -c "DELETE FROM users WHERE login <> 'computer';"
psql "postgresql://postgres:postgres@localhost:5432/tictactoe" -c "TRUNCATE TABLE games, users;"
