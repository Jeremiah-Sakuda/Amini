import logging
import os

from pydantic_settings import BaseSettings

logger = logging.getLogger("amini.config")


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./amini.db"
    cors_origins: list[str] = ["http://localhost:5173"]
    debug: bool = True
    payload_storage_mode: str = "local"  # local | external (future)
    api_keys: list[str] = ["dev-key"]
    retention_days: int = 90
    pool_size: int = 5
    max_overflow: int = 10
    pool_recycle: int = 3600

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

if settings.api_keys == ["dev-key"] and not settings.debug:
    logger.warning(
        "Running with default API key 'dev-key' in non-debug mode. "
        "Set API_KEYS environment variable for production."
    )
