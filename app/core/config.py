"""loads settings from env and exposes cached config."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Football Match Intelligence API"
    environment: str = "development"
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/football_api"
    )
    data_source: str = "Kaggle"
    dataset_name: str = "Football Events Dataset"
    dataset_version: str = "secareanualin-public"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
