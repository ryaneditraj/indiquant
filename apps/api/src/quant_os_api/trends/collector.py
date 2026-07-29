"""Trends collectors — fixture (offline) and optional pytrends live pulls."""

from __future__ import annotations

import hashlib
import math
import time
from datetime import UTC, datetime, timedelta
from typing import Any, Callable

import numpy as np
import pandas as pd

from quant_os_api.trends import CAVEATS
from quant_os_api.trends import store as trends_store
from quant_os_api.trends.universe import (
    comparison_groups,
    entity_config,
    iter_queries,
    trends_config,
)

INDIA_STATES = [
    "Maharashtra",
    "Gujarat",
    "Telangana",
    "Karnataka",
    "Rajasthan",
    "Madhya Pradesh",
    "Tamil Nadu",
    "Andhra Pradesh",
    "Delhi",
    "Uttar Pradesh",
    "West Bengal",
    "Kerala",
    "Punjab",
    "Haryana",
    "Other",
]

WINDOW_DAYS = {"30d": 30, "90d": 90, "12m": 365, "5y": 365 * 5}


def _seed(term: str, window: str, group: str) -> int:
    h = hashlib.sha256(f"{term}|{window}|{group}".encode()).hexdigest()
    return int(h[:8], 16)


def _synthetic_series(
    term: str,
    *,
    window: str,
    query_type: str,
    n: int,
    end: datetime | None = None,
) -> pd.DataFrame:
    """Generate relative 0–100 interest series with seasonality + noise."""
    rng = np.random.default_rng(_seed(term, window, query_type))
    end = end or datetime.now(UTC)
    # Weekly points for longer windows; daily for short
    freq_days = 1 if WINDOW_DAYS[window] <= 90 else 7
    dates = [end - timedelta(days=freq_days * i) for i in range(n)][::-1]

    base = {
        "brand": 55,
        "transactional": 42,
        "category": 60,
        "competitor": 48,
        "risk": 18,
    }.get(query_type, 40)

    # Term-specific offset
    offset = (_seed(term, "x", "y") % 21) - 10
    values: list[float] = []
    level = float(base + offset)
    for i, _ in enumerate(dates):
        seasonal = 8 * math.sin(2 * math.pi * i / max(12, n / 4))
        # Festival bump near Diwali-ish indices for long series
        festival = 12 if (i % max(26, n // 4) == max(20, n // 5)) else 0
        shock = float(rng.normal(0, 3.5))
        # Mild upward drift for brand/tx; competitors mixed
        drift = 0.04 if query_type in {"brand", "transactional"} else (-0.02 if query_type == "risk" else 0.01)
        level = max(0.0, min(100.0, level + drift + shock * 0.15))
        values.append(max(0.0, min(100.0, level + seasonal + festival + shock)))

    # Re-scale to 0–100 within window (Trends-like relative max)
    arr = np.asarray(values, dtype=float)
    mx = float(arr.max()) if len(arr) else 1.0
    if mx > 0:
        arr = (arr / mx) * 100.0
    return pd.DataFrame({"date": [d.date().isoformat() for d in dates], "interest": arr})


def _region_snapshot(entity_id: str, term: str, *, window: str) -> list[dict[str, Any]]:
    cfg = entity_config(entity_id)
    weights = cfg.get("store_weights") or {}
    rng = np.random.default_rng(_seed(term, window, "region"))
    rows: list[dict[str, Any]] = []
    raw_scores: list[float] = []
    for state in INDIA_STATES:
        w = float(weights.get(state, weights.get("Other", 0.05)))
        noise = float(rng.uniform(0.7, 1.3))
        raw_scores.append(max(1.0, 100.0 * w * noise))
    mx = max(raw_scores) or 1.0
    for state, score in zip(INDIA_STATES, raw_scores, strict=True):
        rows.append(
            {
                "region": state,
                "geo_level": "state",
                "interest": round(100.0 * score / mx, 2),
            }
        )
    return rows


def _related_snapshot(term: str, query_type: str) -> list[dict[str, Any]]:
    brand = term.split()[0] if term else "Brand"
    rising_tx = [
        (f"{brand} offers today", 140),
        (f"{brand} coupon", 90),
        ("grocery delivery near me", 75),
        (f"{brand} stock price", 40),
        (f"{brand} franchise", 25),
    ]
    top = [
        (term, 100),
        (f"{brand} online", 72),
        (f"{brand} near me", 55),
        ("supermarket near me", 48),
        ("Blinkit", 44),
    ]
    rows: list[dict[str, Any]] = []
    for q, v in top:
        rows.append({"mode": "top", "related_query": q, "value": v, "value_type": "index"})
    for q, v in rising_tx:
        rows.append(
            {
                "mode": "rising",
                "related_query": q,
                "value": v,
                "value_type": "percent_rise",
                "is_transactional": any(
                    k in q.lower() for k in ("offer", "coupon", "delivery", "near me", "app")
                ),
            }
        )
    if query_type == "risk":
        rows.append(
            {
                "mode": "rising",
                "related_query": f"{brand} delivery late",
                "value": 110,
                "value_type": "percent_rise",
                "is_transactional": False,
            }
        )
    return rows


def collect_fixture(
    entity_id: str = "dmart",
    *,
    windows: list[str] | None = None,
    repeats: int | None = None,
) -> dict[str, Any]:
    """Offline collector that mimics Trends channels with PIT metadata."""
    cfg = trends_config()
    # Always include a long window so PIT earnings backtests have history.
    requested = list(windows or cfg.get("windows") or ["30d", "90d", "12m", "5y"])
    if "5y" not in requested:
        requested = [*requested, "5y"]
    windows = requested
    repeats = int(repeats if repeats is not None else cfg.get("collect_repeats", 3))
    run_id = trends_store.new_run_id()
    collected_at = datetime.now(UTC).isoformat()
    queries = iter_queries(entity_id)
    groups = comparison_groups(entity_id)

    interest_rows: list[dict[str, Any]] = []
    region_rows: list[dict[str, Any]] = []
    related_rows: list[dict[str, Any]] = []

    # Collect per comparison group to preserve shared-normalization context
    term_to_type = {q["term"]: q["query_type"] for q in queries}

    for group in groups:
        g_id = group["group_id"]
        for window in windows:
            n = max(12, WINDOW_DAYS[window] // (1 if WINDOW_DAYS[window] <= 90 else 7))
            # Repeated pulls → average (sampling noise)
            series_by_term: dict[str, list[np.ndarray]] = {t: [] for t in group["terms"]}
            for rep in range(repeats):
                for term in group["terms"]:
                    qtype = term_to_type.get(term, "brand")
                    frame = _synthetic_series(term, window=window, query_type=qtype, n=n)
                    # Small sampling jitter per repeat
                    jitter = np.random.default_rng(_seed(term, window, f"rep{rep}")).normal(
                        0, 1.2, size=len(frame)
                    )
                    vals = np.clip(frame["interest"].to_numpy() + jitter, 0, 100)
                    # Re-normalize within group+window+repeat (shared request)
                    series_by_term[term].append(vals)

            # Align dates from first term
            first_term = group["terms"][0]
            base_frame = _synthetic_series(
                first_term,
                window=window,
                query_type=term_to_type.get(first_term, "brand"),
                n=n,
            )
            dates = base_frame["date"].tolist()

            # Average repeats, then re-scale group max to 100
            averaged: dict[str, np.ndarray] = {}
            for term, reps in series_by_term.items():
                averaged[term] = np.mean(np.vstack(reps), axis=0)
            group_max = max(float(v.max()) for v in averaged.values()) or 1.0
            for term, arr in averaged.items():
                scaled = (arr / group_max) * 100.0
                qtype = term_to_type.get(term, "anchor")
                for date, val in zip(dates, scaled, strict=True):
                    interest_rows.append(
                        {
                            "run_id": run_id,
                            "collected_at": collected_at,
                            "entity_id": entity_id,
                            "geo": cfg.get("geo", "IN"),
                            "window": window,
                            "query_group": g_id,
                            "query_group_role": group.get("role"),
                            "term": term,
                            "query_type": qtype,
                            "date": date,
                            "interest": round(float(val), 3),
                            "is_absolute_volume": False,
                            "provider": "fixture",
                            "repeats_averaged": repeats,
                        }
                    )

            # Regions + related for primary brand term once per window
            brand_term = next(
                (t for t in group["terms"] if term_to_type.get(t) == "brand"),
                group["terms"][0],
            )
            if group.get("role") in {"brand", "competitor"}:
                for reg in _region_snapshot(entity_id, brand_term, window=window):
                    region_rows.append(
                        {
                            "run_id": run_id,
                            "collected_at": collected_at,
                            "entity_id": entity_id,
                            "geo": cfg.get("geo", "IN"),
                            "window": window,
                            "query_group": g_id,
                            "term": brand_term,
                            "provider": "fixture",
                            **reg,
                        }
                    )
            if group.get("role") == "brand" and window in {"90d", "12m"}:
                for rel in _related_snapshot(brand_term, "brand"):
                    related_rows.append(
                        {
                            "run_id": run_id,
                            "collected_at": collected_at,
                            "entity_id": entity_id,
                            "geo": cfg.get("geo", "IN"),
                            "window": window,
                            "query_group": g_id,
                            "seed_term": brand_term,
                            "provider": "fixture",
                            **rel,
                        }
                    )

    trends_store.write_raw_interest(entity_id, run_id=run_id, rows=interest_rows)
    if region_rows:
        trends_store.write_raw_region(entity_id, run_id=run_id, rows=region_rows)
    if related_rows:
        trends_store.write_raw_related(entity_id, run_id=run_id, rows=related_rows)

    return {
        "run_id": run_id,
        "entity_id": entity_id,
        "provider": "fixture",
        "collected_at": collected_at,
        "windows": windows,
        "repeats_averaged": repeats,
        "interest_rows": len(interest_rows),
        "region_rows": len(region_rows),
        "related_rows": len(related_rows),
        "query_groups": [g["group_id"] for g in groups],
        "caveats": CAVEATS,
        "is_absolute_volume": False,
    }


def collect_entity(
    entity_id: str = "dmart",
    *,
    provider: str | None = None,
    windows: list[str] | None = None,
) -> dict[str, Any]:
    cfg = trends_config()
    provider = provider or str(cfg.get("default_provider", "fixture"))
    if provider == "fixture":
        return collect_fixture(entity_id, windows=windows)
    if provider == "pytrends":
        try:
            return _collect_pytrends(entity_id, windows=windows)
        except Exception as exc:  # noqa: BLE001 — fall back with explicit warning
            result = collect_fixture(entity_id, windows=windows)
            result["provider"] = "fixture"
            result["live_error"] = str(exc)
            result["warning"] = "pytrends unavailable or failed; used fixture. Live Trends not absolute volume."
            return result
    raise ValueError(f"Unknown trends provider: {provider}")


def _is_rate_limit_error(exc: BaseException) -> bool:
    text = str(exc).lower()
    markers = ("429", "rate limit", "too many requests", "quota", "response code 429")
    return any(m in text for m in markers)


def call_with_backoff(
    fn: Callable[[], Any],
    *,
    retries: int = 3,
    base_delay_sec: float = 2.0,
    sleep_fn: Callable[[float], None] = time.sleep,
    label: str = "pytrends",
) -> Any:
    """Retry callable on rate-limit / transient failures with exponential backoff."""
    last_exc: BaseException | None = None
    attempts = max(1, int(retries))
    for attempt in range(attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 — live provider surface is noisy
            last_exc = exc
            retryable = _is_rate_limit_error(exc) or attempt < attempts - 1
            if not retryable or attempt >= attempts - 1:
                break
            delay = float(base_delay_sec) * (2**attempt)
            sleep_fn(delay)
    assert last_exc is not None
    raise RuntimeError(f"{label} failed after {attempts} attempts: {last_exc}") from last_exc


def _collect_pytrends(entity_id: str, *, windows: list[str] | None = None) -> dict[str, Any]:
    """Optional live path — requires optional dependency pytrends."""
    try:
        from pytrends.request import TrendReq  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError("Install optional extra: pip install pytrends") from exc

    cfg = trends_config()
    windows = windows or list(cfg.get("windows") or ["90d"])
    geo = str(cfg.get("geo", "IN"))
    run_id = trends_store.new_run_id()
    collected_at = datetime.now(UTC).isoformat()
    retries = int(cfg.get("pytrends_retries", 3))
    base_delay = float(cfg.get("pytrends_backoff_sec", 2.0))
    inter_request_delay = float(cfg.get("pytrends_request_gap_sec", 1.0))
    pytrends = TrendReq(hl="en-IN", tz=330)
    groups = comparison_groups(entity_id)
    queries = iter_queries(entity_id)
    term_to_type = {q["term"]: q["query_type"] for q in queries}

    timeframe_map = {
        "30d": "today 1-m",
        "90d": "today 3-m",
        "12m": "today 12-m",
        "5y": "today 5-y",
    }

    interest_rows: list[dict[str, Any]] = []
    region_rows: list[dict[str, Any]] = []
    related_rows: list[dict[str, Any]] = []
    request_count = 0

    for group in groups:
        for window in windows:
            if request_count > 0 and inter_request_delay > 0:
                time.sleep(inter_request_delay)
            tf = timeframe_map.get(window, "today 3-m")
            terms = group["terms"][:5]  # Trends comparison limit

            def _fetch_iot() -> Any:
                pytrends.build_payload(terms, timeframe=tf, geo=geo)
                return pytrends.interest_over_time()

            iot = call_with_backoff(
                _fetch_iot,
                retries=retries,
                base_delay_sec=base_delay,
                label=f"pytrends interest_over_time[{group['group_id']}/{window}]",
            )
            request_count += 1
            if iot is None or iot.empty:
                continue
            for term in terms:
                if term not in iot.columns:
                    continue
                for ts, val in iot[term].items():
                    interest_rows.append(
                        {
                            "run_id": run_id,
                            "collected_at": collected_at,
                            "entity_id": entity_id,
                            "geo": geo,
                            "window": window,
                            "query_group": group["group_id"],
                            "query_group_role": group.get("role"),
                            "term": term,
                            "query_type": term_to_type.get(term, "anchor"),
                            "date": str(pd.Timestamp(ts).date()),
                            "interest": float(val),
                            "is_absolute_volume": False,
                            "provider": "pytrends",
                            "repeats_averaged": 1,
                        }
                    )
            try:
                ibr = call_with_backoff(
                    lambda: pytrends.interest_by_region(resolution="REGION", inc_low_vol=True),
                    retries=retries,
                    base_delay_sec=base_delay,
                    label="pytrends interest_by_region",
                )
                request_count += 1
                brand_term = terms[0]
                if ibr is not None and not ibr.empty and brand_term in ibr.columns:
                    for region, row in ibr.iterrows():
                        region_rows.append(
                            {
                                "run_id": run_id,
                                "collected_at": collected_at,
                                "entity_id": entity_id,
                                "geo": geo,
                                "window": window,
                                "query_group": group["group_id"],
                                "term": brand_term,
                                "region": str(region),
                                "geo_level": "state",
                                "interest": float(row[brand_term]),
                                "provider": "pytrends",
                            }
                        )
            except Exception:  # noqa: BLE001
                pass
            try:
                related = call_with_backoff(
                    pytrends.related_queries,
                    retries=retries,
                    base_delay_sec=base_delay,
                    label="pytrends related_queries",
                )
                request_count += 1
                seed = terms[0]
                if related and seed in related:
                    for mode in ("top", "rising"):
                        frame = related[seed].get(mode)
                        if frame is None or frame.empty:
                            continue
                        for _, r in frame.head(10).iterrows():
                            related_rows.append(
                                {
                                    "run_id": run_id,
                                    "collected_at": collected_at,
                                    "entity_id": entity_id,
                                    "geo": geo,
                                    "window": window,
                                    "query_group": group["group_id"],
                                    "seed_term": seed,
                                    "mode": mode,
                                    "related_query": str(r.get("query", "")),
                                    "value": float(r.get("value", 0) or 0),
                                    "value_type": "index" if mode == "top" else "percent_rise",
                                    "provider": "pytrends",
                                }
                            )
            except Exception:  # noqa: BLE001
                pass

    if not interest_rows:
        raise RuntimeError("pytrends returned empty interest series")

    trends_store.write_raw_interest(entity_id, run_id=run_id, rows=interest_rows)
    if region_rows:
        trends_store.write_raw_region(entity_id, run_id=run_id, rows=region_rows)
    if related_rows:
        trends_store.write_raw_related(entity_id, run_id=run_id, rows=related_rows)

    return {
        "run_id": run_id,
        "entity_id": entity_id,
        "provider": "pytrends",
        "collected_at": collected_at,
        "windows": windows,
        "interest_rows": len(interest_rows),
        "region_rows": len(region_rows),
        "related_rows": len(related_rows),
        "pytrends_requests": request_count,
        "pytrends_retries": retries,
        "caveats": CAVEATS,
        "is_absolute_volume": False,
    }
