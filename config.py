# app/core/config.py
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "api.rennesdev.fr"
    APP_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    DEBUG: bool = True
    ENVIRONMENT: str = "local"

    CORS_ORIGINS: list[str] = ["*"]

    API_KEY: str = "change-me"
    WEBHOOK_SHARED_SECRET: str = "change-me-too"

    N8N_BASE_URL: str = "https://n8n.example.com"
    N8N_LEADS_WEBHOOK_URL: str = ""
    N8N_QUOTES_WEBHOOK_URL: str = ""
    N8N_ORDERS_WEBHOOK_URL: str = ""

    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    STORAGE_DIR: str = "storage"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()