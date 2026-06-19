from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str
    redis_url: str = "redis://localhost:6379/0"
    chat_model: str = "gpt-4o-mini"
    worker_poll_seconds: int = 2


settings = Settings()
