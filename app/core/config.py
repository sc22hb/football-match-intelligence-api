"""loads settings from env and exposes cached config."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Football Match Intelligence API"
    environment: str = "development"
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/football_api"
    )
    data_source: str = "Fantasy Premier League API"
    dataset_name: str = "Premier League 2025/26"
    dataset_version: str = "fpl-element-summary-live"
    api_key: str = "dev-api-key"
    rate_limit_window_seconds: int = 60
    rate_limit_max_requests: int = 1000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
