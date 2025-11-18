FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

ARG MONGO_CONNECTION_STRING
ARG MONGO_CONNECTION_STRING

ENV MONGO_CONNECTION_STRING=$MONGO_CONNECTION_STRING \
    MONGO_CONNECTION_STRING=$MONGO_CONNECTION_STRING

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src ./src

RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.accounts.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]