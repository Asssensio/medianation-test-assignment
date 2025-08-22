"""
Minimal blog API: FastAPI + PostgreSQL (psycopg 3).
Фокус на инфраструктуре: простые операции без ORM, файловое логирование.
"""

import os
import logging
from typing import List

import psycopg
from fastapi import FastAPI
from pydantic import BaseModel

# ---------- Схемы публичных данных ----------
class Post(BaseModel):
    id: int
    title: str
    content: str

class CreatePostRequest(BaseModel):
    title: str
    content: str

# ---------- Логирование ----------
LOG_DIR = os.getenv("LOG_DIR", "/logs/app")
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, "app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(),  # дублирование в stdout для docker logs
    ],
)
logger = logging.getLogger(__name__)

# ---------- Параметры подключения к БД ----------
DB_HOST = os.getenv("POSTGRES_HOST")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")

# В проде не допускаем запуск без пароля
if not DB_PASS:
    raise RuntimeError("POSTGRES_PASSWORD is not set")

# Порт по умолчанию 5432; при необходимости добавить POSTGRES_PORT
DSN = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

def get_conn():
    """Одно подключение на запрос; для тестового задания пул не используем."""
    return psycopg.connect(DSN, autocommit=True)

def init_db():
    """Создаёт минимально необходимую схему данных."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL
                );
            """)
    logger.info("Database initialized: table 'posts' ready")

# ---------- Приложение ----------
app = FastAPI()

@app.on_event("startup")
def on_startup():
    """Инициализация базы при старте приложения."""
    init_db()
    logger.info("Application started")

@app.get("/posts", response_model=List[Post])
def get_posts():
    """Возвращает список публикаций (упорядочено по id)."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, content FROM posts ORDER BY id;")
            rows = cur.fetchall()
            return [Post(id=r[0], title=r[1], content=r[2]) for r in rows]

@app.post("/posts", response_model=Post)
def create_post(post_request: CreatePostRequest):
    """Создаёт публикацию и возвращает её с присвоенным id."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO posts (title, content) VALUES (%s, %s) RETURNING id;",
                (post_request.title, post_request.content),
            )
            new_id = cur.fetchone()[0]
            logger.info("Post created: id=%s title=%s", new_id, post_request.title)
            return Post(id=new_id, title=post_request.title, content=post_request.content)
