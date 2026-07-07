from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    database_url: str = "postgresql+asyncpg://chat:chat@localhost:5432/chat"
    host: str = "0.0.0.0"
    port: int = 8001
    log_level: str = "INFO"


settings = Settings()
