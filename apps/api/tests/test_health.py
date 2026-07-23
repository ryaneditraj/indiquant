"""API smoke + research pipeline tests."""

from __future__ import annotations

from datetime import date

import pandas as pd

from quant_os_api.plugins.data.fixture import FixtureDataProvider
from quant_os_api.quant.backtest import sma_crossover_signals
from quant_os_api.quant.metrics import compute_metrics
from quant_os_api.quant.regimes import current_regime
from quant_os_api.quant.validation import check_lookahead, validate_strategy


def test_health_ok(client) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app_name"]


def test_public_settings(client) -> None:
    response = client.get("/api/v1/settings/public")
    assert response.status_code == 200
    assert "has_openai_compatible_key" in response.json()["settings"]["ai"]


def test_dashboard_snapshot(client) -> None:
    response = client.get("/api/v1/dashboard/snapshot")
    assert response.status_code == 200
    assert "system_health" in response.json()


def test_crud_hypothesis_strategy_experiment(client) -> None:
    h = client.post(
        "/api/v1/hypotheses",
        json={
            "title": "Momentum persists",
            "thesis": "Winners keep winning on NSE",
            "rationale": "Classic TSMOM",
            "family": "momentum",
            "tags": ["momentum"],
        },
    )
    assert h.status_code == 200
    hid = h.json()["id"]

    s = client.post(
        "/api/v1/strategies",
        json={"name": "sma-demo", "idea": "SMA", "hypothesis_id": hid, "code": "sma()"},
    )
    assert s.status_code == 200
    sid = s.json()["id"]

    e = client.post(
        "/api/v1/experiments",
        json={"strategy_id": sid, "status": "queued", "ai_summary": "pending"},
    )
    assert e.status_code == 200
    assert client.get(f"/api/v1/experiments/{e.json()['id']}").status_code == 200


def test_ingest_and_datasets(client, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("QUANT_OS_CONFIG_PATH", str(tmp_path))
    # Use default parquet under repo; ingest via fixture provider
    response = client.post(
        "/api/v1/data/ingest",
        json={
            "symbol": "RELIANCE",
            "start": "2024-01-01",
            "end": "2024-02-01",
            "provider": "fixture",
        },
    )
    assert response.status_code == 200
    assert response.json()["rows"] > 0
    datasets = client.get("/api/v1/datasets")
    assert datasets.status_code == 200
    assert any(d["symbol"] == "RELIANCE" for d in datasets.json()["datasets"])


def test_research_cycle(client) -> None:
    response = client.post(
        "/api/v1/ai/cycle",
        json={"symbol": "TCS", "lookback_days": 120, "seed": 1, "provider": "fixture", "persist": True},
    )
    assert response.status_code == 200
    body = response.json()
    assert "experiment" in body
    assert body["persisted"]["experiment_id"]
    assert len(body["events"]) >= 5


def test_backtest_run(client) -> None:
    response = client.post(
        "/api/v1/backtests/run",
        json={"symbol": "INFY", "family": "momentum", "provider": "fixture", "persist": True},
    )
    assert response.status_code == 200
    body = response.json()
    assert "metrics" in body
    assert "experiment_id" in body


def test_search(client) -> None:
    client.post(
        "/api/v1/hypotheses",
        json={"title": "Gap fade", "thesis": "Gaps mean-revert", "family": "mean_reversion"},
    )
    response = client.get("/api/v1/search", params={"q": "Gap"})
    assert response.status_code == 200
    assert len(response.json()["hypotheses"]) >= 1


def test_chat_offline(client) -> None:
    response = client.post(
        "/api/v1/ai/chat",
        json={"messages": [{"role": "user", "content": "Why did it fail?"}], "experiment_ids": []},
    )
    assert response.status_code == 200
    assert response.json()["mode"] in {"offline", "llm", "error-fallback"}


def test_portfolio(client) -> None:
    response = client.post(
        "/api/v1/portfolio/analyze",
        json={"symbols": ["RELIANCE", "TCS"]},
    )
    assert response.status_code == 200
    assert "correlation" in response.json()


def test_quant_unit_helpers() -> None:
    provider = FixtureDataProvider()
    rows = provider.get_ohlcv("RELIANCE", date(2024, 1, 1), date(2024, 6, 1))
    bars = pd.DataFrame(rows)
    signals = sma_crossover_signals(bars["close"])
    assert check_lookahead(signals, bars["close"])["passed"]
    result = validate_strategy(bars, signals, signal_fn=sma_crossover_signals)
    assert "metrics" in result
    assert current_regime(bars["close"])["regime"]
    equity = pd.Series([1.0, 1.1, 1.05, 1.2])
    assert compute_metrics(equity)["n_bars"] == 4
