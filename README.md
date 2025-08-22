## **Mini Blog API - FastAPI · Uvicorn · PostgreSQL · psycopg3 · Docker/Compose · GitHub Actions**

`GET /posts` — список публикаций
`POST /posts` — сoзданиe публикации

---------------------------------------------------------------------------------------

**Список технологий**

* FastAPI, Uvicorn
* PostgreSQL, psycopg (v3)
* Docker, Docker Compose
* GitHub Actions (CI/CD)

---------------------------------------------------------------------------------------

**Быстрый старт (локально)**

1. Создайте `.env` в корне:

```
POSTGRES_HOST=db
POSTGRES_DB=blog_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=change_me
```

2. (Опционально) подготовьте точки логов:

```
mkdir -p logs/app logs/postgres
```

3. Запуск:

```
docker compose up -d --build
```

4. Проверка:

* Swagger UI: [http://localhost:8080/docs](http://localhost:8080/docs)
* Журнал приложения: `docker compose logs -f app`
* Остановка: `docker compose down`

---------------------------------------------------------------------------------------

**Описание API (примеры запросов/ответов)**

`GET /posts`

Ответ 200:

```
[]
```

`POST /posts`

Пример запроса:

```
{"title":"Hello","content":"World"}
```

Пример ответа 200:

```
{"id":1,"title":"Hello","content":"World"}
```

Примеры команд:

```
curl -X POST http://localhost:8080/posts \
  -H 'Content-Type: application/json' \
  -d '{"title":"Hello","content":"World"}'

curl http://localhost:8080/posts
```

---

**Данные и логи**

* Данные БД: volume `pgdata` (`/var/lib/postgresql/data`).
* Логи приложения: на хосте `./logs/app/app.log`.
* Логи PostgreSQL: на хосте `./logs/postgres` (включена файловая запись и суточная ротация).

---

**Smoke‑тест**

```
# после запуска локально или деплоя на сервер
curl -X POST http://<host>:8080/posts \
  -H 'Content-Type: application/json' \
  -d '{"title":"Smoke","content":"Test"}'

curl http://<host>:8080/posts
# ожидаем увидеть созданную запись в списке
```

---------------------------------------------------------------------------------------

**CI/CD**

Пайплайн `.github/workflows/deploy.yml` при пуше в `main`:

1. Сборка Docker‑образа и push в Docker Hub: `${DOCKERHUB_USERNAME}/medianation-app:latest`
2. Подключение по SSH к серверу, генерация `.env`
3. `docker pull` + `docker compose -f docker-compose.prod.yml up -d`

**Secrets:**

* `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`
* `SERVER_HOST`, `SERVER_PORT`, `SERVER_USER`, `SSH_PRIVATE_KEY`
* `POSTGRES_PASSWORD`

**Variables:**

* `PROJECT_DIR` (пример: `/opt/medianation-app`)
* `POSTGRES_DB` (пример: `blog_db`)
* `POSTGRES_USER` (пример: `admin`)

**Требования к серверу**

* Установлены Docker и Docker Compose
* Пользователь в группе `docker`
* Каталог `${PROJECT_DIR}` существует и доступен пользователю

---------------------------------------------------------------------------------------

**Структура**

```
├─ app/main.py                  # FastAPI + psycopg
├─ logs/                        # для логов
├─ Dockerfile                   # образ приложения
├─ docker-compose.yml           # dev: build из исходников
├─ docker-compose.prod.yml      # prod: запуск готового образа
└─ .github/workflows/deploy.yml # CI/CD
```
