"""
config.py
---------
Centralized application configuration using Pydantic Settings.

All configuration values are sourced from environment variables (via a .env
file in local development, or real environment variables in production).
No secrets are ever hardcoded in source code.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    Values are read from environment variables. See `.env.example` for the
    full list of supported variables and their descriptions.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # General application settings
    # ------------------------------------------------------------------
    APP_NAME: str = "AI REST API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development | staging | production
    DEBUG: bool = True

    # ------------------------------------------------------------------
    # Server settings
    # ------------------------------------------------------------------
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ------------------------------------------------------------------
    # OpenAI settings
    # ------------------------------------------------------------------
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = "gpt-4.1-mini"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_OUTPUT_TOKENS: int = 1024
    OPENAI_TIMEOUT_SECONDS: int = 60

    # ------------------------------------------------------------------
    # Authentication settings
    # ------------------------------------------------------------------
    API_KEY: str = Field(default="")
    JWT_SECRET_KEY: str = Field(default="change-me-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    # ------------------------------------------------------------------
    # Database settings
    # ------------------------------------------------------------------
    DATABASE_URL: str = "sqlite:///./ai_rest_api.db"

    # ------------------------------------------------------------------
    # CORS settings
    # ------------------------------------------------------------------
    CORS_ORIGINS: str = "*"

    # ------------------------------------------------------------------
    # Rate limiting settings
    # ------------------------------------------------------------------
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ------------------------------------------------------------------
    # Logging settings
    # ------------------------------------------------------------------
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, value: str) -> str:
        return value

    @property
    def cors_origins_list(self) -> List[str]:
        """Return CORS_ORIGINS as a parsed list of origins."""
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.

    Using lru_cache ensures the .env file / environment is only parsed once
    per process, and the same Settings object is reused across the app via
    dependency injection.
    """
    return Settings()


settings = get_settings()
