"""Pytest fixtures — isolated SQLite DB per session."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# Must set before importing app modules that cache settings/engine
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault(
    "QUANT_OS_CONFIG_PATH",
    str(Path(__file__).resolve().parents[3] / "config.yaml"),
)


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("QUANT_OS_CONFIG_PATH", str(Path(__file__).resolve().parents[3] / "config.yaml"))

    from quant_os_api.config import get_settings
    from quant_os_api.db import get_engine, get_session_factory, init_db

    get_settings.cache_clear()
    get_engine.cache_clear()
    get_session_factory.cache_clear()
    init_db()

    from fastapi.testclient import TestClient

    from quant_os_api.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client

    get_settings.cache_clear()
    get_engine.cache_clear()
    get_session_factory.cache_clear()
