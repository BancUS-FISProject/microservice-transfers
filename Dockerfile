FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Default configuration via environment variables
ENV MONGO_CONNECTION_STRING=mongodb://mongo:27017 \
    MONGO_DATABASE_NAME=transactions_db \
    ACCOUNTS_SERVICE_URL=http://host.docker.internal:8000

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src ./src

RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "uvicorn src.transfers.app:create_app --factory --host 0.0.0.0 --port ${PORT:-8000}"]