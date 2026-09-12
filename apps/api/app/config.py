"""
Saarthi Finance — Application Configuration.

Loads settings from environment variables / .env file using pydantic-settings.
"""

from __future__ import annotations

import json
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


from pathlib import Path

_API_DIR = Path(__file__).resolve().parent.parent
_DEFAULT_DB_FILE = _API_DIR / "saarthi.db"


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- Database ----
    database_url: str = f"sqlite:///{_DEFAULT_DB_FILE.as_posix()}"

    # ---- CORS ----
    cors_origins: str = '["http://localhost:3000","http://localhost:5173"]'

    @property
    def cors_origin_list(self) -> List[str]:
        """Parse CORS origins from JSON string."""
        try:
            return json.loads(self.cors_origins)
        except (json.JSONDecodeError, TypeError):
            return ["http://localhost:3000"]

    # ---- JWT ----
    jwt_secret: str = "saarthi-demo-secret-change-in-prod"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # ---- LLM ----
    llm_api_key: str = ""

    # ---- General ----
    log_level: str = "INFO"
    environment: str = "development"


settings = Settings()
