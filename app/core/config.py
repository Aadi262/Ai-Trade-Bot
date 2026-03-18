from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    SECRET_KEY: str
    TRADING_MODE: str = Field(default="paper", pattern=r"^(paper|live)$")
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str
    POSTGRES_USER: str = "tradingbot"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "tradingbot"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Anthropic
    ANTHROPIC_API_KEY: str

    # Zerodha Kite (Phase 2)
    KITE_API_KEY: str = ""
    KITE_API_SECRET: str = ""
    KITE_ACCESS_TOKEN: str = ""

    # News & Data
    NEWSAPI_KEY: str = ""

    # Monitoring
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    SENTRY_DSN: str = ""

    # Auth
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_IN: int = 86400

    # Rate limiting
    RATE_LIMIT_SCAN_PER_MINUTE: int = 10
    RATE_LIMIT_SIGNAL_PER_MINUTE: int = 60


settings = Settings()  # type: ignore[call-arg]
