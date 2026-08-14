"""Additional v0.2 API coverage."""

from __future__ import annotations

import time


def test_seed_and_datasets(client) -> None:
    seeded = client.post("/api/v1/admin/seed")
    assert seeded.status_code == 200
    assert len(seeded.json()["seeded"]) >= 3
    datasets = client.get("/api/v1/datasets")
    assert datasets.status_code == 200
    assert len(datasets.json()["datasets"]) >= 1


def test_notebook_execute(client) -> None:
    code = (
        "provider = FixtureDataProvider()\n"
        "rows = provider.get_ohlcv('RELIANCE', date(2024,1,1), date(2024,3,1))\n"
        "bars = pd.DataFrame(rows)\n"
        "result = {'n': len(bars)}\n"
        "print(result)\n"
    )
    response = client.post("/api/v1/notebook/execute", json={"code": code})
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["result"]["n"] > 0


def test_notebook_blocks_os(client) -> None:
    response = client.post("/api/v1/notebook/execute", json={"code": "import os\nos.system('echo hi')"})
    assert response.status_code == 200
    assert response.json()["ok"] is False


def test_research_loop_start_stop(client) -> None:
    from quant_os_api.services.research_loop import reset_loop_controller

    reset_loop_controller()
    started = client.post(
        "/api/v1/ai/loop/start",
        json={
            "symbols": ["RELIANCE"],
            "provider": "fixture",
            "interval_seconds": 0.5,
            "max_cycles": 1,
        },
    )
    assert started.status_code == 200
    assert started.json()["status"] in {"running", "stopped"}
    # Wait for cycle
    for _ in range(30):
        status = client.get("/api/v1/ai/loop").json()
        if status["cycles_completed"] >= 1 or status["status"] == "stopped":
            break
        time.sleep(0.3)
    stopped = client.post("/api/v1/ai/loop/stop")
    assert stopped.status_code == 200
    final = client.get("/api/v1/ai/loop").json()
    assert final["cycles_completed"] >= 1


def test_duckdb_sync_and_query(client) -> None:
    client.post("/api/v1/admin/seed")
    synced = client.post("/api/v1/analytics/sync")
    assert synced.status_code == 200
    assert synced.json()["dataset_count"] >= 1
    view = synced.json()["registered_views"][0]
    queried = client.post(
        "/api/v1/analytics/query",
        json={"sql": f"SELECT count(*) AS n FROM {view}"},
    )
    assert queried.status_code == 200
    assert queried.json()["rows"][0]["n"] > 0


def test_csv_provider_listed(client) -> None:
    providers = client.get("/api/v1/data/providers").json()["providers"]
    names = {p["name"] for p in providers}
    assert "csv_local" in names


def test_duckdb_rejects_stacked_sql(client) -> None:
    client.post("/api/v1/admin/seed")
    client.post("/api/v1/analytics/sync")
    stacked = client.post(
        "/api/v1/analytics/query",
        json={"sql": "SELECT 1; DROP TABLE experiment"},
    )
    assert stacked.status_code == 400


def test_encrypt_helpers_disabled_in_production(client, monkeypatch) -> None:
    from quant_os_api.config import get_settings

    monkeypatch.setenv("QUANT_OS_ENV", "production")
    get_settings.cache_clear()
    response = client.post("/api/v1/security/encrypt", json={"value": "demo"})
    assert response.status_code == 403
    get_settings.cache_clear()
