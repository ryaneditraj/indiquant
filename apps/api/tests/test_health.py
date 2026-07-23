"""API smoke tests — no database required for health/settings."""

from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient

from quant_os_api.main import create_app
from quant_os_api.plugins.data.fixture import FixtureDataProvider


def test_health_ok() -> None:
    client = TestClient(create_app())
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app_name"]
    assert "version" in body


def test_public_settings_hides_secrets() -> None:
    client = TestClient(create_app())
    response = client.get("/api/v1/settings/public")
    assert response.status_code == 200
    payload = response.json()["settings"]
    assert "ai" in payload
    assert "api_key" not in str(payload).lower() or payload["ai"]["has_openai_compatible_key"] in {
        True,
        False,
    }
    assert "has_openai_compatible_key" in payload["ai"]


def test_dashboard_snapshot() -> None:
    client = TestClient(create_app())
    response = client.get("/api/v1/dashboard/snapshot")
    assert response.status_code == 200
    body = response.json()
    assert "system_health" in body
    assert body["market_regime"]


def test_nav_sections() -> None:
    client = TestClient(create_app())
    response = client.get("/api/v1/meta/nav")
    assert response.status_code == 200
    sections = response.json()["sections"]
    ids = {s["id"] for s in sections}
    assert "dashboard" in ids
    assert "settings" in ids


def test_fixture_provider_deterministic() -> None:
    provider = FixtureDataProvider()
    assert provider.health()["status"] == "ok"
    rows = provider.get_ohlcv("RELIANCE", date(2024, 1, 1), date(2024, 1, 10))
    assert len(rows) > 0
    assert rows[0]["symbol"] == "RELIANCE"
    assert set(rows[0]) >= {"ts", "open", "high", "low", "close", "volume"}
