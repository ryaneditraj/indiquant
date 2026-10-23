"""Guards for path traversal, analytics file reads, and local-only tools."""

from __future__ import annotations

import pytest


def test_ingest_rejects_path_traversal_symbol(client) -> None:
    response = client.post(
        "/api/v1/data/ingest",
        json={
            "symbol": "../etc",
            "start": "2024-01-01",
            "end": "2024-01-10",
            "timeframe": "1d",
            "provider": "fixture",
        },
    )
    assert response.status_code == 400


def test_symbol_and_entity_helpers_reject_dotdot() -> None:
    from quant_os_api.safe_ids import UnsafePathError, safe_entity_id, safe_symbol, safe_timeframe
    from quant_os_api.trends.store import entity_dir

    with pytest.raises(UnsafePathError):
        safe_symbol("..")
    with pytest.raises(UnsafePathError):
        safe_timeframe("../x")
    with pytest.raises(UnsafePathError):
        safe_entity_id("../etc")
    with pytest.raises(UnsafePathError):
        entity_dir("../etc")


def test_trends_export_rejects_unsafe_entity_id(client) -> None:
    response = client.get("/api/v1/trends/bad-id/export")
    assert response.status_code == 400


def test_duckdb_rejects_file_reads(client) -> None:
    client.post("/api/v1/admin/seed")
    synced = client.post("/api/v1/analytics/sync")
    assert synced.status_code == 200
    leaked = client.post(
        "/api/v1/analytics/query",
        json={"sql": "SELECT * FROM read_parquet('/etc/passwd')"},
    )
    assert leaked.status_code == 400
    direct = client.post(
        "/api/v1/analytics/query",
        json={"sql": "SELECT * FROM 'data/sample_csv/RELIANCE.csv'"},
    )
    assert direct.status_code == 400


def test_notebook_blocks_dunder_escape(client) -> None:
    code = "result = ''.__class__.__mro__[1].__subclasses__()\n"
    response = client.post("/api/v1/notebook/execute", json={"code": code})
    assert response.status_code == 200
    assert response.json()["ok"] is False


def test_notebook_and_seed_disabled_in_production(client, monkeypatch) -> None:
    from quant_os_api.config import get_settings

    monkeypatch.setenv("QUANT_OS_ENV", "production")
    get_settings.cache_clear()
    notebook = client.post("/api/v1/notebook/execute", json={"code": "result = 1"})
    assert notebook.status_code == 403
    seeded = client.post("/api/v1/admin/seed")
    assert seeded.status_code == 403
    get_settings.cache_clear()


def test_search_escapes_like_wildcards(client) -> None:
    client.post(
        "/api/v1/hypotheses",
        json={"title": "Gap fade", "thesis": "Gaps mean-revert", "family": "mean_reversion"},
    )
    response = client.get("/api/v1/search", params={"q": "%"})
    assert response.status_code == 200
    titles = [row["title"] for row in response.json()["hypotheses"]]
    assert "Gap fade" not in titles


def test_csv_cells_neutralize_formulas() -> None:
    from quant_os_api.routes import _csv_cell

    assert _csv_cell("=HYPERLINK(\"http://evil\")") == "'=HYPERLINK(\"http://evil\")"
    assert _csv_cell(12.5) == 12.5
    assert _csv_cell("relative_index") == "relative_index"


def test_attachment_filename_strips_header_injection() -> None:
    from quant_os_api.routes import _attachment_filename

    name = _attachment_filename('trends-dmart-90d\r\nX-Evil: 1".csv')
    assert "\r" not in name
    assert "\n" not in name
    assert '"' not in name


def test_production_refuses_placeholder_secret(monkeypatch) -> None:
    from quant_os_api.config import enforce_production_secrets, get_settings

    monkeypatch.setenv("QUANT_OS_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "change-me")
    get_settings.cache_clear()
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        enforce_production_secrets(get_settings())
    get_settings.cache_clear()
