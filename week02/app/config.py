from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional, Union

from pydantic import AnyHttpUrl, Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "dev"
    TESTING = "test"
    PRODUCTION = "prod"


class DatabaseSettings(BaseSettings):
    path: Path = Field(default=Path("data/app.db"))
    timeout: int = Field(default=30, description="SQLite connection timeout in seconds")
    check_same_thread: bool = Field(default=False, description="SQLite check_same_thread flag")

    @property
    def connection_string(self) -> str:
        return f"sqlite:///{self.path}"

    @field_validator("path", mode="before")
    @classmethod
    def validate_path(cls, v: Any) -> Path:
        if isinstance(v, str):
            return Path(v)
        return v


class OllamaSettings(BaseSettings):
    model: str = Field(default="llama3.1:8b")
    base_url: AnyHttpUrl = Field(default="http://localhost:11434")
    timeout: int = Field(default=60, description="Timeout in seconds for Ollama API calls")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)

    @field_validator("base_url", mode="before")
    @classmethod
    def validate_base_url(cls, v: Any) -> AnyHttpUrl:
        if isinstance(v, str):
            # Ensure URL ends without trailing slash
            v = v.rstrip("/")
        return v


class LoggingSettings(BaseSettings):
    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    date_format: str = Field(default="%Y-%m-%d %H:%M:%S")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False)

    # Application
    app_name: str = Field(default="Action Item Extractor")
    app_version: str = Field(default="1.0.0")
    api_prefix: str = Field(default="")
    docs_url: str = Field(default="/docs")
    redoc_url: str = Field(default="/redoc")

    # Security
    cors_origins: Union[List[str], str] = Field(default=["*"])
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: Union[List[str], str] = Field(default=["*"])
    cors_allow_headers: Union[List[str], str] = Field(default=["*"])

    # Sub-configurations
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    # Project paths
    base_dir: Path = Field(default=Path(__file__).resolve().parents[1])
    data_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1] / "data")

    @field_validator("cors_origins", "cors_allow_methods", "cors_allow_headers", mode="before")
    @classmethod
    def validate_cors_list_fields(cls, v: Any) -> List[str]:
        """Convert string to list for CORS list fields."""
        if isinstance(v, str):
            # Handle empty string
            if not v.strip():
                return []
            # Try to parse as JSON first (for backward compatibility with JSON format)
            try:
                import json

                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed]
            except (json.JSONDecodeError, TypeError):
                # If not JSON, treat as comma-separated string
                pass
            # Split by comma and strip whitespace
            return [item.strip() for item in v.split(",") if item.strip()]
        elif isinstance(v, list):
            # Already a list, ensure all items are strings
            return [str(item).strip() for item in v]
        # For any other type (shouldn't happen), return empty list
        return []

    @field_validator("data_dir", mode="before")
    @classmethod
    def validate_data_dir(cls, v: Any, info: Any) -> Path:
        if isinstance(v, str):
            v = Path(v)
        if not v.is_absolute():
            # Make relative to base_dir
            base_dir = info.data.get("base_dir", Path(__file__).resolve().parents[1])
            v = base_dir / v
        return v

    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        return self.environment == Environment.TESTING

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION


def get_settings() -> Settings:
    """Get application settings based on environment."""
    env_file = f".env.{os.getenv('ENVIRONMENT', 'dev')}"

    # Check if environment-specific .env file exists
    if Path(env_file).exists():
        return Settings(_env_file=env_file)

    return Settings()


# Global settings instance
settings = get_settings()
