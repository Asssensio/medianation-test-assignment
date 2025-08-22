# Базовый слой
FROM python:3.12-slim

# Поведение интерпретатора внутри контейнера
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Системные зависимости и актуальный pip
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --upgrade pip

# Приложение
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app .

# Веб-сервер для FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
