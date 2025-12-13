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

    # Throttling Configuration
    THROTTLE_CPU_WARNING: float = 70.0
    THROTTLE_CPU_CRITICAL: float = 85.0
    THROTTLE_MEMORY_WARNING: float = 75.0
    THROTTLE_MEMORY_CRITICAL: float = 90.0
    THROTTLE_MAX_CONCURRENT: int = 100
    THROTTLE_WARNING_CONCURRENT: int = 75

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
