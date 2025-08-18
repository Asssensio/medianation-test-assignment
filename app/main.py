from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# --- Модели данных ---
# Описываем, как выглядят наши "посты" в блоге
class Post(BaseModel):
    id: int
    title: str
    content: str

# Описываем, какие данные мы ждем при создании нового поста
class CreatePostRequest(BaseModel):
    title: str
    content: str

# --- "База данных" ---
# Пока что будем хранить все посты в простом списке в памяти
db: List[Post] = []
post_id_counter = 0

# --- Приложение FastAPI ---
app = FastAPI()

# --- Эндпоинты (наши URL) ---

@app.get("/posts", response_model=List[Post])
def get_posts():
    """Возвращает список всех постов."""
    return db

@app.post("/posts", response_model=Post)
def create_post(post_request: CreatePostRequest):
    """Создает новый пост."""
    global post_id_counter
    post_id_counter += 1
    
    new_post = Post(
        id=post_id_counter,
        title=post_request.title,
        content=post_request.content
    )
    db.append(new_post)
    return new_post