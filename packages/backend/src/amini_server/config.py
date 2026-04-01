from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./amini.db"
    cors_origins: list[str] = ["http://localhost:5173"]
    debug: bool = True
    payload_storage_mode: str = "local"  # local | external (future)
    api_keys: list[str] = ["dev-key"]
    retention_days: int = 90

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
