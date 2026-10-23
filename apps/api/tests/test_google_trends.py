"""Google Trends Intelligence — Phase 1+2 + modeling tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from quant_os_api.main import app
from quant_os_api.trends.collector import collect_fixture
from quant_os_api.trends.cross_signals import load_cross_signals
from quant_os_api.trends.features import compute_features
from quant_os_api.trends.modeling import predict_entity, rank_entities, train_models
from quant_os_api.trends.score import score_entity
from quant_os_api.trends.universe import comparison_groups, iter_queries, list_entities

client = TestClient(app)


def test_query_universe_buckets() -> None:
    qs = iter_queries("dmart")
    types = {q["query_type"] for q in qs}
    assert types == {"brand", "transactional", "category", "competitor", "risk"}
    assert any(q["term"] == "DMart" for q in qs)
    assert any(q["term"] == "Blinkit" for q in qs)
    groups = comparison_groups("dmart")
    assert any(g["group_id"] == "competitor_basket" for g in groups)


def test_phase2_entities_configured() -> None:
    ids = set(list_entities())
    expected = {
        "dmart",
        "trent",
        "reliance_smart",
        "jiomart",
        "bigbasket",
        "blinkit",
        "zepto",
        "nykaa",
        "titan",
    }
    assert expected <= ids
    for eid in ("trent", "blinkit", "nykaa"):
        qs = iter_queries(eid)
        assert {q["query_type"] for q in qs} == {
            "brand",
            "transactional",
            "category",
            "competitor",
            "risk",
        }


def test_collect_and_score_fixture() -> None:
    collected = collect_fixture("dmart", windows=["90d"], repeats=2)
    assert collected["is_absolute_volume"] is False
    assert collected["interest_rows"] > 0
    assert collected["region_rows"] > 0
    scored = score_entity("dmart", window="90d")
    assert scored["ok"] is True
    assert scored["is_absolute_volume"] is False
    assert 0 <= scored["search_demand_score"] <= 100
    assert scored["quality_badge"] in {"high", "medium", "low", "unreliable"}
    assert set(scored["components"]) >= {
        "brand_attention",
        "purchase_intent",
        "regional_strength",
        "competitive_share",
        "risk_friction",
        "signal_quality",
    }
    f = scored["features"]
    assert "qoq_growth" in f
    assert "yoy_seasonal" in f
    assert "festival_adjusted_change" in f
    assert "search_confirmation_composite" in f
    assert f.get("corr_satellite") is not None or f.get("corr_app_rank") is not None


def test_cross_signal_fixtures() -> None:
    collect_fixture("dmart", windows=["90d"], repeats=1)
    xs = load_cross_signals("dmart", window="90d")
    assert xs["is_absolute_volume"] is False
    assert "panel" in xs
    for key in ("satellite", "app_rank", "pricing_promo", "hiring"):
        assert key in xs["panel"]
        assert xs["panel"][key]["latest"] is not None


def test_multi_entity_collect_score() -> None:
    for eid in ("trent", "blinkit"):
        c = collect_fixture(eid, windows=["90d"], repeats=1)
        assert c["interest_rows"] > 0
        s = score_entity(eid, window="90d")
        assert s["ok"] is True
        assert s["entity_id"] == eid


def test_modeling_train_predict_rank() -> None:
    collect_fixture("dmart", windows=["90d", "5y"], repeats=1)
    collect_fixture("trent", windows=["90d", "5y"], repeats=1)
    trained = train_models(entity_ids=["dmart", "trent"])
    assert trained["ok"] is True
    assert trained["meta"]["proxy_labels"] is True
    pred = predict_entity("dmart", window="90d")
    assert pred["ok"] is True
    assert pred["proxy_labels"] is True
    assert "revenue_growth" in pred["predictions"]
    assert "nowcast_momentum" in pred["predictions"]
    assert pred["predictions"]["revenue_growth"]["confidence_interval"]["method"]
    ranked = rank_entities(["dmart", "trent"], window="90d")
    assert ranked["ok"] is True
    assert len(ranked["rankings"]) >= 1


def test_trends_http_flow() -> None:
    r = client.post(
        "/api/v1/trends/collect",
        json={"entity_id": "dmart", "provider": "fixture", "windows": ["90d", "5y"]},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["is_absolute_volume"] is False

    d = client.get("/api/v1/trends/dmart/dashboard")
    assert d.status_code == 200
    dash = d.json()
    assert dash["ok"] is True
    assert "caveats" in dash
    assert dash["score"]["search_demand_score"] is not None
    assert dash["cross_signal"]["panel"]["satellite"]["latest"] is not None

    a = client.get("/api/v1/trends/dmart/alerts")
    assert a.status_code == 200

    b = client.post("/api/v1/trends/dmart/backtest")
    assert b.status_code == 200
    bt = b.json()
    assert bt["ok"] is True
    assert "guards" in bt

    ex = client.get("/api/v1/trends/dmart/export")
    assert ex.status_code == 200
    assert ex.json()["is_absolute_volume"] is False
    assert ex.json()["export_format"] == "json"

    csv_ex = client.get("/api/v1/trends/dmart/export?format=csv")
    assert csv_ex.status_code == 200
    assert "text/csv" in csv_ex.headers.get("content-type", "")
    csv_body = csv_ex.text
    assert "search_demand_score" in csv_body
    assert "relative_index_not_absolute_volume" in csv_body
    assert "is_absolute_volume" in csv_body.splitlines()[0]

    ents = client.get("/api/v1/trends/entities")
    assert ents.status_code == 200
    assert len(ents.json()["entities"]) >= 9


def test_export_empty_entity_fails_soft() -> None:
    r = client.get("/api/v1/trends/not_a_real_entity_xyz/export")
    assert r.status_code in {400, 404}
    csv_r = client.get("/api/v1/trends/not_a_real_entity_xyz/export?format=csv")
    assert csv_r.status_code in {400, 404}


def test_pytrends_backoff_retries_rate_limit() -> None:
    from quant_os_api.trends.collector import call_with_backoff

    sleeps: list[float] = []
    attempts = {"n": 0}

    def flaky() -> str:
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("429 Too Many Requests")
        return "ok"

    out = call_with_backoff(
        flaky,
        retries=4,
        base_delay_sec=0.5,
        sleep_fn=sleeps.append,
        label="test",
    )
    assert out == "ok"
    assert attempts["n"] == 3
    assert sleeps == [0.5, 1.0]


def test_pytrends_backoff_exhausts() -> None:
    from quant_os_api.trends.collector import call_with_backoff

    def always_fail() -> None:
        raise RuntimeError("rate limit exceeded")

    try:
        call_with_backoff(always_fail, retries=2, base_delay_sec=0.1, sleep_fn=lambda _d: None)
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "failed after 2 attempts" in str(exc)


def test_trends_modeling_http() -> None:
    client.post(
        "/api/v1/trends/collect",
        json={"entity_id": "dmart", "provider": "fixture", "windows": ["90d", "5y"]},
    )
    client.post(
        "/api/v1/trends/collect",
        json={"entity_id": "nykaa", "provider": "fixture", "windows": ["90d", "5y"]},
    )
    tr = client.post("/api/v1/trends/models/train", json={"entity_ids": ["dmart", "nykaa"]})
    assert tr.status_code == 200
    assert tr.json()["ok"] is True

    pred = client.get("/api/v1/trends/dmart/predict")
    assert pred.status_code == 200
    assert pred.json()["ok"] is True

    nc = client.get("/api/v1/trends/dmart/nowcast")
    assert nc.status_code == 200
    assert nc.json()["ok"] is True

    cmp_ = client.get("/api/v1/trends/comparison")
    assert cmp_.status_code == 200
    assert cmp_.json()["ok"] is True

    cmp_csv = client.get("/api/v1/trends/comparison?format=csv")
    assert cmp_csv.status_code == 200
    assert "text/csv" in cmp_csv.headers.get("content-type", "")
    header = cmp_csv.text.splitlines()[0]
    assert "ranking_score" in header
    assert "side_hint" in header
    assert "relative_index_not_absolute_volume" in cmp_csv.text


def test_features_missing_data_message() -> None:
    # Unknown entity raises
    try:
        compute_features("not_a_real_entity_xyz")
        raise AssertionError("expected KeyError")
    except KeyError:
        pass


def test_score_unknown_entity_no_data() -> None:
    """Configured entity with empty store should fail soft, not crash."""
    scored = score_entity("titan", window="90d")
    # May be ok if prior tests collected titan; if empty, must be soft failure.
    if not scored.get("ok"):
        assert scored.get("error")
        assert scored.get("is_absolute_volume") is not True
        assert "caveats" in scored or "score" in scored or "error" in scored


def test_rank_empty_and_partial_universe() -> None:
    """Ranking with no collected entities returns empty list, not an exception."""
    empty = rank_entities(["not_configured_entity_zzz"], window="90d")
    assert empty["ok"] is True
    assert empty["n"] == 0
    assert empty["rankings"] == []
    assert empty["is_absolute_volume"] is False
    assert empty.get("empty_state") is True
    assert empty.get("next_steps")
    assert any("absolute" in c.lower() or "relative" in c.lower() for c in empty["caveats"])

    collect_fixture("dmart", windows=["90d"], repeats=1)
    partial = rank_entities(["dmart", "not_configured_entity_zzz"], window="90d")
    assert partial["ok"] is True
    assert partial["n"] >= 1
    assert all(r.get("rank") for r in partial["rankings"])
    assert all(r.get("side_hint") in {"long", "short", "neutral", "watch"} for r in partial["rankings"])
    assert "demand_fallback" in (partial.get("ranking_methods_used") or []) or partial["rankings"][0].get(
        "ranking_method"
    ) in {"demand_fallback", "model"}


def test_rank_quality_tiebreak_and_watch() -> None:
    collect_fixture("dmart", windows=["90d", "5y"], repeats=1)
    collect_fixture("trent", windows=["90d", "5y"], repeats=1)
    ranked = rank_entities(["dmart", "trent"], window="90d")
    assert ranked["ok"] is True
    assert ranked["n"] == 2
    ranks = [r["rank"] for r in ranked["rankings"]]
    assert ranks == list(range(1, ranked["n"] + 1))
    # Scores must be non-increasing
    scores = [float(r["ranking_score"]) for r in ranked["rankings"]]
    assert scores == sorted(scores, reverse=True)
    for r in ranked["rankings"]:
        assert r.get("is_absolute_volume") is False
        assert r.get("ranking_method") in {"model", "demand_fallback"}


def test_collect_rejects_bad_provider_softly() -> None:
    r = client.post(
        "/api/v1/trends/collect",
        json={"entity_id": "dmart", "provider": "not_a_provider"},
    )
    assert r.status_code == 400
    assert "provider" in r.json()["detail"].lower() or "Unknown" in r.json()["detail"]


def test_comparison_csv_empty_soft() -> None:
    """Empty rankings still return header-only CSV (soft success)."""
    r = client.get(
        "/api/v1/trends/comparison?format=csv&window=90d",
    )
    # May have data from prior tests — always soft 200 with relative-index note
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")
    lines = r.text.strip().splitlines()
    assert lines[0].startswith("rank,entity_id")
    assert "is_absolute_volume" in lines[0]
    assert "relative_index_not_absolute_volume" in r.text or len(lines) == 1


def test_fundamentals_stub_returns_none() -> None:
    from quant_os_api.trends.fundamentals import load_labels

    assert load_labels("dmart", as_of="2024-01-01") is None


def test_dashboard_missing_entity_soft_failure() -> None:
    d = client.get("/api/v1/trends/not_a_real_entity_xyz/dashboard")
    assert d.status_code == 200
    body = d.json()
    assert body.get("ok") is False
    assert body.get("empty_state") is True
    assert body.get("is_absolute_volume") is False
    assert body.get("caveats")
    assert body.get("next_steps")
