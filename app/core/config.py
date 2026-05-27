from functools import lru_cache
import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    app_name: str = Field(default="gameops-agent-test-platform")
    api_prefix: str = Field(default="/api")
    debug: bool = Field(default=False)


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "gameops-agent-test-platform"),
        api_prefix=os.getenv("API_PREFIX", "/api"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )
