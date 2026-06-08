from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "api-rennesdev"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "dev"

    API_KEY: str = "change-me"

    N8N_LEADS_WEBHOOK_URL: str = ""
    N8N_QUOTES_WEBHOOK_URL: str = ""
    N8N_ORDERS_WEBHOOK_URL: str = ""

    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()