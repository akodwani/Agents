"""Application configuration models and environment loading utilities."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings loaded from environment variables."""

    openai_api_key: SecretStr | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: SecretStr | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    google_api_key: SecretStr | None = Field(default=None, alias="GOOGLE_API_KEY")

    max_budget_usd: float = Field(default=100.0, alias="MAX_BUDGET_USD", ge=0)
    warning_budget_ratio: float = Field(default=0.8, alias="WARNING_BUDGET_RATIO", ge=0, le=1)
    hard_stop_budget_ratio: float = Field(default=1.0, alias="HARD_STOP_BUDGET_RATIO", ge=0, le=2)

    min_confidence_threshold: float = Field(default=0.65, alias="MIN_CONFIDENCE_THRESHOLD", ge=0, le=1)
    escalation_threshold: float = Field(default=0.45, alias="ESCALATION_THRESHOLD", ge=0, le=1)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()
