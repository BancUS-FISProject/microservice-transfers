from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGO_CONNECTION_STRING: str = "mongodb://localhost:27017"
    MONGO_DATABASE_NAME: str = "transactions_db"

    # URL base del servicio de accounts (puede ser sobreescrito por entorno y debe lanzarse el servicio de accounts para poder acceder)
    ACCOUNTS_SERVICE_URL: str = "http://host.docker.internal:8000"

    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "log.txt"
    LOG_BACKUP_COUNT: int = 7

    BREAKER_FAILS: int = 5
    BREAKER_TIMEOUT: int = 60

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    CACHE_TTL: int = 3600

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
