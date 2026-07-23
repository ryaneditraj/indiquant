"""Application settings loaded from environment + config.yaml."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _repo_root() -> Path:
    """Resolve monorepo root from this file: apps/api/src/quant_os_api/config.py."""
    return Path(__file__).resolve().parents[4]


def load_yaml_config(path: Path | None = None) -> dict[str, Any]:
    if path is not None:
        config_path = path
    elif os.getenv("QUANT_OS_CONFIG_PATH"):
        config_path = Path(os.environ["QUANT_OS_CONFIG_PATH"])
    else:
        config_path = _repo_root() / "config.yaml"

    if not config_path.is_absolute():
        cwd_candidate = (Path.cwd() / config_path).resolve()
        root_candidate = (_repo_root() / config_path).resolve()
        if cwd_candidate.exists():
            config_path = cwd_candidate
        elif root_candidate.exists():
            config_path = root_candidate
        else:
            config_path = cwd_candidate

    if not config_path.exists():
        return {}
    with config_path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config root must be a mapping: {config_path}")
    return data


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    quant_os_env: str = Field(default="development", alias="QUANT_OS_ENV")
    quant_os_config_path: str = Field(default="", alias="QUANT_OS_CONFIG_PATH")

    database_url: str = Field(
        default="postgresql+psycopg://quant:quant@localhost:5432/quant_os",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    celery_broker_url: str = Field(default="", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="", alias="CELERY_RESULT_BACKEND")

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="API_CORS_ORIGINS",
    )

    secret_key: str = Field(default="change-me", alias="SECRET_KEY")

    ai_openai_compatible_base_url: str = Field(
        default="https://api.openai.com/v1",
        alias="AI_OPENAI_COMPATIBLE_BASE_URL",
    )
    ai_openai_compatible_api_key: str = Field(default="", alias="AI_OPENAI_COMPATIBLE_API_KEY")
    ai_default_provider: str = Field(default="openai_compatible", alias="AI_DEFAULT_PROVIDER")
    ai_default_model: str = Field(default="gpt-4o-mini", alias="AI_DEFAULT_MODEL")
    ai_local_base_url: str = Field(default="http://localhost:11434/v1", alias="AI_LOCAL_BASE_URL")
    ai_local_api_key: str = Field(default="", alias="AI_LOCAL_API_KEY")

    yaml_config: dict[str, Any] = Field(default_factory=dict, exclude=True)

    def model_post_init(self, __context: Any) -> None:
        path = Path(self.quant_os_config_path) if self.quant_os_config_path else None
        object.__setattr__(self, "yaml_config", load_yaml_config(path))

    @property
    def app_name(self) -> str:
        return str(self.yaml_config.get("app", {}).get("name", "Research OS"))

    @property
    def app_tagline(self) -> str:
        return str(
            self.yaml_config.get("app", {}).get(
                "tagline", "AI Quantitative Research Operating System"
            )
        )

    @property
    def cors_origin_list(self) -> list[str]:
        yaml_origins = self.yaml_config.get("api", {}).get("cors_origins")
        if isinstance(yaml_origins, list) and yaml_origins:
            return [str(o) for o in yaml_origins]
        return [o.strip() for o in self.api_cors_origins.split(",") if o.strip()]

    @property
    def broker_url(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def result_backend(self) -> str:
        return self.celery_result_backend or self.redis_url

    def public_info(self) -> dict[str, Any]:
        """Non-secret settings snapshot for the Settings / health UI."""
        features = self.yaml_config.get("features", {})
        ui = self.yaml_config.get("ui", {})
        return {
            "env": self.quant_os_env,
            "app_name": self.app_name,
            "tagline": self.app_tagline,
            "primary_market": self.yaml_config.get("app", {}).get("primary_market", "IN"),
            "timezone": self.yaml_config.get("app", {}).get("default_timezone", "Asia/Kolkata"),
            "ai": {
                "default_provider": self.ai_default_provider,
                "default_model": self.ai_default_model,
                "openai_compatible_base_url": self.ai_openai_compatible_base_url,
                "has_openai_compatible_key": bool(self.ai_openai_compatible_api_key),
                "local_base_url": self.ai_local_base_url,
            },
            "data_providers": self.yaml_config.get("data_providers", {}),
            "brokers": self.yaml_config.get("brokers", {}),
            "features": features,
            "ui": ui,
            "backtest_defaults": self.yaml_config.get("backtest", {}),
            "validation": self.yaml_config.get("validation", {}),
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
