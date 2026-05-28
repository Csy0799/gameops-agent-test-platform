from functools import lru_cache
import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    app_name: str = Field(default="gameops-agent-test-platform")
    api_prefix: str = Field(default="/api")
    debug: bool = Field(default=False)
    operation_log_retention_days: int = Field(default=365)
    enable_operation_log: bool = Field(default=True)


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "gameops-agent-test-platform"),
        api_prefix=os.getenv("API_PREFIX", "/api"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        operation_log_retention_days=int(
            os.getenv("OPERATION_LOG_RETENTION_DAYS", "365")
        ),
        enable_operation_log=os.getenv("ENABLE_OPERATION_LOG", "true").lower()
        == "true",
    )
