"""loads settings from env and exposes cached config."""

from functools import lru_cache

from pydantic import field_validator
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

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://") and "+psycopg" not in value:
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
