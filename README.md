# Mini Blog API — FastAPI · PostgreSQL · Docker · GitHub Actions

`GET /posts` — список публикаций
`POST /posts` — создание публикации

[![CI/CD](https://github.com/Asssensio/medianation-test-assignment/actions/workflows/deploy.yml/badge.svg?branch=main)](https://github.com/Asssensio/medianation-test-assignment/actions/workflows/deploy.yml)

---

## Live demo

* Swagger UI (prod): **[http://45.141.78.45:8080/docs](http://45.141.78.45:8080/docs)**
* Быстрый тест:

  ```bash
  curl -sS -X POST http://45.141.78.45:8080/posts \
    -H 'Content-Type: application/json' \
    -d '{"title":"Hello","content":"World"}'

  curl -sS http://45.141.78.45:8080/posts
  ```

> Примечание: demo-сервер учебный; база может периодически очищаться.

---

## Технологии

* FastAPI, Uvicorn
* PostgreSQL + psycopg3
* Docker & Docker Compose
* GitHub Actions (CI/CD)

---

## Локальный запуск

1. Создайте `.env` в корне:

```env
POSTGRES_HOST=db
POSTGRES_DB=blog_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=change_me
```

2. (Опционально) подготовьте папки логов:

```bash
mkdir -p logs/app logs/postgres
```

3. Запуск:

```bash
docker compose up -d --build
```

4. Проверка:

* Swagger: [http://localhost:8080/docs](http://localhost:8080/docs)
* Логи приложения: `docker compose logs -f app`
* Остановка: `docker compose down`

---

## API

### GET /posts → 200

```json
[
  { "id": 1, "title": "Hello", "content": "World" }
]
```

### POST /posts → 200

Request:

```json
{ "title": "Hello", "content": "World" }
```

Response:

```json
{ "id": 1, "title": "Hello", "content": "World" }
```

CLI примеры:

```bash
curl -sS -X POST http://localhost:8080/posts \
  -H 'Content-Type: application/json' \
  -d '{"title":"Hello","content":"World"}'

curl -sS http://localhost:8080/posts
```

---

## Данные и логи

* Данные БД: volume `pgdata` → `/var/lib/postgresql/data` (переживают перезапуск).
* Логи приложения: `./logs/app/app.log` (монтирование `/logs/app`).
* Логи PostgreSQL: `./logs/postgres` (включён `logging_collector` + ротация).

---

## Smoke‑тест

```bash
# после локального запуска или деплоя на сервер
curl -sS -X POST http://<host>:8080/posts \
  -H 'Content-Type: application/json' \
  -d '{"title":"Smoke","content":"Test"}'

curl -sS http://<host>:8080/posts
# запись должна появиться в списке
```

---

## CI/CD (GitHub Actions)

Пайплайн `.github/workflows/deploy.yml` срабатывает на `push` в `main`:

1. **CI:** собирает Docker-образ и пушит в Docker Hub → `${DOCKERHUB_USERNAME}/medianation-app:latest`.
2. **CD:** по SSH заходит на сервер, генерирует `.env` из Secrets/Variables, делает `docker pull` и `docker compose -f docker-compose.prod.yml up -d`.
3. **Smoke-тест:** `curl http://127.0.0.1:8080/posts` на сервере. Если недоступно — job падает.

Запустить деплой вручную:

```bash
git commit --allow-empty -m "ci: trigger"
git push
```

### Secrets (Settings → Secrets and variables → Actions)

* `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`
* `SERVER_HOST`, `SERVER_PORT`, `SERVER_USER`, `SSH_PRIVATE_KEY`
* `POSTGRES_PASSWORD`

### Variables

* `PROJECT_DIR` (напр. `/opt/medianation-app`)
* `POSTGRES_DB` (напр. `blog_db`)
* `POSTGRES_USER` (напр. `admin`)

### Требования к серверу

* Docker + Docker Compose установлены, пользователь в группе `docker`
* Папка `${PROJECT_DIR}` существует и доступна
* Открыт порт `8080` (или проброшен в файрволле)

---

## Структура проекта

```
├─ app/main.py                  # FastAPI + psycopg3 (без ORM)
├─ logs/                        # точки монтирования логов
├─ Dockerfile                   # образ приложения
├─ docker-compose.yml           # dev: сборка из исходников
├─ docker-compose.prod.yml      # prod: запуск готового образа
└─ .github/workflows/deploy.yml # CI/CD
```