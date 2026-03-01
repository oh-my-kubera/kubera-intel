"""Application settings."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def intel_dir() -> Path:
    """Return the .intel data directory, creating it if needed."""
    d = Path(".intel")
    d.mkdir(exist_ok=True)
    return d


def reports_dir() -> Path:
    """Return the .intel/reports directory."""
    d = intel_dir() / "reports"
    d.mkdir(exist_ok=True)
    return d


def data_dir() -> Path:
    """Return the .intel/data directory."""
    d = intel_dir() / "data"
    d.mkdir(exist_ok=True)
    return d


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="INTEL_",
        env_file=".intel/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    dart_max_results: int = 20
    naver_max_results: int = 20
    gemini_model: str = "gemini-2.0-flash"
    report_lang: str = "ko"
    debug: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


def setup_logging(debug: bool = False) -> None:
    """Configure logging for kubera-intel. Call once at CLI entry."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=level,
    )
    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
