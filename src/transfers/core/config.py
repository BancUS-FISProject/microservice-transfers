from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Default settings
    MONGO_CONNECTION_STRING: str = "mongodb://localhost:27017"
    MONGO_DATABASE_NAME: str = "transactions_db"

    # URL base del servicio de accounts (puede ser sobreescrito por entorno)
    ACCOUNTS_SERVICE_URL: str = "http://host.docker.internal:8000"

    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "log.txt"
    LOG_BACKUP_COUNT: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
