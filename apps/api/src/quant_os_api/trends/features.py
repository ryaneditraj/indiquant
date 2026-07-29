"""Feature engineering on relative Trends indices (never absolute volume)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

import numpy as np
import pandas as pd

from quant_os_api.trends import store as trends_store
from quant_os_api.trends.universe import entity_config


def _to_as_of(as_of: str | None) -> str:
    if as_of:
        return as_of
    return datetime.now(UTC).date().isoformat()


def _series_for(
    interest: pd.DataFrame,
    *,
    term: str | None = None,
    query_type: str | None = None,
    window: str = "90d",
    query_group: str | None = None,
) -> pd.Series:
    frame = interest[interest["window"] == window].copy()
    if query_group:
        frame = frame[frame["query_group"] == query_group]
    if term:
        frame = frame[frame["term"] == term]
    if query_type:
        frame = frame[frame["query_type"] == query_type]
    if frame.empty:
        return pd.Series(dtype=float)
    # Prefer latest run for PIT consistency
    if "run_id" in frame.columns:
        latest = frame["run_id"].max()
        frame = frame[frame["run_id"] == latest]
    frame = frame.groupby("date", as_index=False)["interest"].mean().sort_values("date")
    return pd.Series(frame["interest"].to_numpy(dtype=float), index=pd.to_datetime(frame["date"]))


def _growth(series: pd.Series, periods: int) -> float | None:
    if len(series) <= periods:
        return None
    a, b = float(series.iloc[-1]), float(series.iloc[-1 - periods])
    if b == 0:
        return None
    return (a - b) / abs(b)


def _ma(series: pd.Series, window: int) -> float | None:
    if len(series) < window:
        return None
    return float(series.iloc[-window:].mean())


def _slope(series: pd.Series, window: int = 8) -> float | None:
    if len(series) < window:
        return None
    y = series.iloc[-window:].to_numpy(dtype=float)
    x = np.arange(len(y), dtype=float)
    return float(np.polyfit(x, y, 1)[0])


def _accel(series: pd.Series, window: int = 8) -> float | None:
    if len(series) < window + 2:
        return None
    s1 = _slope(series.iloc[:-1], window)
    s2 = _slope(series, window)
    if s1 is None or s2 is None:
        return None
    return s2 - s1


def _zscore(series: pd.Series, lookback: int = 52) -> float | None:
    if len(series) < max(8, lookback // 4):
        return None
    hist = series.iloc[-lookback:]
    mu, sigma = float(hist.mean()), float(hist.std(ddof=1) or 0.0)
    if sigma == 0:
        return 0.0
    return (float(series.iloc[-1]) - mu) / sigma


def _volatility(series: pd.Series, window: int = 12) -> float | None:
    if len(series) < window:
        return None
    return float(series.iloc[-window:].std(ddof=1) or 0.0)


def _spike(series: pd.Series, z_thresh: float = 2.0) -> dict[str, Any]:
    z = _zscore(series, lookback=min(52, max(8, len(series))))
    spiked = z is not None and z >= z_thresh
    decay = None
    if spiked and len(series) >= 4:
        peak_idx = int(np.argmax(series.iloc[-8:].to_numpy()))
        tail = series.iloc[-8 + peak_idx :]
        if len(tail) >= 2 and float(tail.iloc[0]) > 0:
            decay = float((tail.iloc[-1] - tail.iloc[0]) / abs(tail.iloc[0]))
    return {"spike_detected": bool(spiked), "spike_z": z, "post_spike_decay": decay}


def _sparsity(series: pd.Series) -> dict[str, Any]:
    if series.empty:
        return {"sparse": True, "zero_share": 1.0, "unstable": True}
    zero_share = float((series <= 1e-6).mean())
    unstable = zero_share > 0.35 or float(series.std(ddof=1) or 0) < 0.5
    return {"sparse": zero_share > 0.25, "zero_share": zero_share, "unstable": unstable}


# Approximate India festival windows (day-of-year centers ± half-width)
_FESTIVAL_WINDOWS = (
    (45, 10),   # Holi ~ early Mar
    (230, 12),  # Ganesh / Onam cluster
    (295, 14),  # Diwali / festive retail peak
    (359, 8),   # Year-end / New Year
)


def _in_festival(ts: pd.Timestamp) -> bool:
    doy = int(ts.dayofyear)
    for center, half in _FESTIVAL_WINDOWS:
        lo, hi = center - half, center + half
        if lo <= doy <= hi or (lo < 1 and doy >= 365 + lo):
            return True
    return False


def _qoq_growth(series: pd.Series) -> float | None:
    """Quarter-to-date average versus prior quarter-to-date average."""
    if len(series) < 20:
        return None
    idx = pd.DatetimeIndex(series.index)
    last = idx[-1]
    q = (last.month - 1) // 3 + 1
    year = last.year
    # Current QTD
    q_start_month = 3 * (q - 1) + 1
    q_start = pd.Timestamp(year=year, month=q_start_month, day=1)
    cur = series[(idx >= q_start) & (idx <= last)]
    # Prior quarter full span
    if q == 1:
        pq_start = pd.Timestamp(year=year - 1, month=10, day=1)
        pq_end = pd.Timestamp(year=year - 1, month=12, day=31)
        # Align QTD length into prior quarter
        days = (last - q_start).days
        pq_asof = min(pq_end, pq_start + pd.Timedelta(days=days))
    else:
        pq_start_month = 3 * (q - 2) + 1
        pq_start = pd.Timestamp(year=year, month=pq_start_month, day=1)
        days = (last - q_start).days
        pq_asof = pq_start + pd.Timedelta(days=days)
    prior = series[(idx >= pq_start) & (idx <= pq_asof)]
    if cur.empty or prior.empty or float(prior.mean()) == 0:
        return None
    return float(cur.mean() - prior.mean()) / abs(float(prior.mean()))


def _yoy_seasonal(series: pd.Series) -> float | None:
    """Year-over-year seasonal comparison at same calendar window."""
    if len(series) < 30:
        return None
    idx = pd.DatetimeIndex(series.index)
    last = idx[-1]
    # Compare trailing ~28d vs same window prior year when available
    cur_start = last - pd.Timedelta(days=28)
    cur = series[(idx >= cur_start) & (idx <= last)]
    prior_end = last - pd.Timedelta(days=365)
    prior_start = prior_end - pd.Timedelta(days=28)
    prior = series[(idx >= prior_start) & (idx <= prior_end)]
    if cur.empty or prior.empty or float(prior.mean()) == 0:
        # Fallback: compare last point vs ~52 weekly steps back on long series
        if len(series) > 52:
            a, b = float(series.iloc[-1]), float(series.iloc[-53])
            if b == 0:
                return None
            return (a - b) / abs(b)
        return None
    return float(cur.mean() - prior.mean()) / abs(float(prior.mean()))


def _festival_adjusted_change(series: pd.Series) -> float | None:
    """Recent growth excluding festival-window observations (relative index)."""
    if len(series) < 16:
        return None
    mask = pd.Series([not _in_festival(pd.Timestamp(i)) for i in series.index], index=series.index)
    cleaned = series[mask]
    if len(cleaned) < 10:
        cleaned = series
    return _growth(cleaned, min(14, len(cleaned) // 2))


def compute_features(entity_id: str = "dmart", *, as_of: str | None = None, window: str = "90d") -> dict[str, Any]:
    as_of = _to_as_of(as_of)
    cfg = entity_config(entity_id)
    interest = trends_store.read_interest(entity_id, as_of=as_of)
    regions = trends_store.read_regions(entity_id, as_of=as_of)
    related = trends_store.read_related(entity_id, as_of=as_of)

    if interest.empty:
        return {
            "entity_id": entity_id,
            "as_of": as_of,
            "window": window,
            "ok": False,
            "error": "No interest data — run POST /trends/collect first",
            "features": {},
        }

    brand = _series_for(interest, query_type="brand", window=window, query_group="brand_vs_anchor")
    if brand.empty:
        brand = _series_for(interest, query_type="brand", window=window)
    tx = _series_for(interest, query_type="transactional", window=window, query_group="tx_vs_brand")
    if tx.empty:
        tx = _series_for(interest, query_type="transactional", window=window)
    cat = _series_for(interest, query_type="category", window=window)
    risk = _series_for(interest, query_type="risk", window=window, query_group="risk_vs_brand")
    if risk.empty:
        risk = _series_for(interest, query_type="risk", window=window)

    # Competitor basket share inside shared competitor_basket group
    comp_group = interest[
        (interest["window"] == window) & (interest["query_group"] == "competitor_basket")
    ]
    relative_share = None
    relative_strength = None
    if not comp_group.empty:
        latest_run = comp_group["run_id"].max()
        g = comp_group[comp_group["run_id"] == latest_run]
        last_date = g["date"].max()
        snap = g[g["date"] == last_date]
        brand_val = float(snap.loc[snap["query_type"] == "brand", "interest"].mean() or 0)
        comp_val = float(snap.loc[snap["query_type"] == "competitor", "interest"].sum() or 0)
        total = brand_val + comp_val
        relative_share = brand_val / total if total > 0 else None
        relative_strength = (brand_val / comp_val) if comp_val > 0 else None

    brand_to_cat = None
    if len(brand) and len(cat) and float(cat.iloc[-1]) > 0:
        brand_to_cat = float(brand.iloc[-1]) / float(cat.iloc[-1])
    tx_to_brand = None
    if len(tx) and len(brand) and float(brand.iloc[-1]) > 0:
        tx_to_brand = float(tx.iloc[-1]) / float(brand.iloc[-1])
    risk_ratio = None
    if len(risk) and len(brand) and float(brand.iloc[-1]) > 0:
        risk_ratio = float(risk.iloc[-1]) / float(brand.iloc[-1])

    # Regional features
    state_weighted = None
    core_vs_noncore = None
    dispersion = None
    concentration = None
    if not regions.empty:
        latest = regions[regions["run_id"] == regions["run_id"].max()]
        latest = latest[latest["window"] == window] if window in set(latest["window"]) else latest
        weights = cfg.get("store_weights") or {}
        core = set(cfg.get("core_states") or [])
        if not latest.empty:
            # average interest by region across terms
            by_reg = latest.groupby("region")["interest"].mean()
            wsum = 0.0
            wtot = 0.0
            for state, val in by_reg.items():
                w = float(weights.get(str(state), weights.get("Other", 0.05)))
                wsum += w * float(val)
                wtot += w
            state_weighted = wsum / wtot if wtot else None
            core_vals = [float(by_reg[s]) for s in core if s in by_reg.index]
            non_vals = [float(v) for s, v in by_reg.items() if s not in core]
            if core_vals and non_vals:
                core_vs_noncore = float(np.mean(core_vals) - np.mean(non_vals))
            vals = by_reg.to_numpy(dtype=float)
            if len(vals):
                dispersion = float(np.std(vals))
                shares = vals / (vals.sum() or 1.0)
                concentration = float(np.sum(shares**2))  # HHI-like

    # Related query breadth / intensity
    breadth = 0
    intensity = None
    if not related.empty and "mode" in related.columns:
        rising = related[related["mode"] == "rising"]
        if not rising.empty:
            if "is_transactional" in rising.columns:
                tx_rising = rising[rising["is_transactional"] == True]  # noqa: E712
            else:
                tx_rising = rising[
                    rising["related_query"].str.contains(
                        "offer|delivery|near me|app|coupon|grocery", case=False, na=False
                    )
                ]
            breadth = int(len(tx_rising))
            if breadth:
                intensity = float(tx_rising["value"].mean())

    spike = _spike(brand) if len(brand) else {"spike_detected": False, "spike_z": None, "post_spike_decay": None}
    sparse = _sparsity(brand)

    # Pre-earnings windows (relative to as_of; caller passes as_of = earnings - N days for backtest)
    def _momentum(days: int) -> float | None:
        if brand.empty:
            return None
        # approximate trading/calendar points
        pts = max(1, days // (1 if window in {"30d", "90d"} else 7))
        return _growth(brand, pts)

    features: dict[str, Any] = {
        "wow_growth": _growth(brand, 1 if window in {"30d", "90d"} else 1),
        "growth_2w": _growth(brand, 14 if window in {"30d", "90d"} else 2),
        "growth_4w": _growth(brand, 28 if window in {"30d", "90d"} else 4),
        "growth_8w": _growth(brand, 56 if window in {"30d", "90d"} else 8),
        "mom_growth": _growth(brand, 30 if window in {"30d", "90d"} else 4),
        "ma_4w": _ma(brand, 28 if window in {"30d", "90d"} else 4),
        "ma_8w": _ma(brand, 56 if window in {"30d", "90d"} else 8),
        "trend_slope": _slope(brand),
        "trend_acceleration": _accel(brand),
        "zscore_1y": _zscore(brand, lookback=min(len(brand), 52 if window != "30d" else 30)),
        "volatility": _volatility(brand),
        **spike,
        "relative_strength_vs_competitors": relative_strength,
        "relative_search_share": relative_share,
        "brand_to_category_ratio": brand_to_cat,
        "transactional_to_brand_ratio": tx_to_brand,
        "risk_query_ratio": risk_ratio,
        "state_weighted_search_score": state_weighted,
        "core_vs_noncore_spread": core_vs_noncore,
        "search_dispersion": dispersion,
        "search_concentration_hhi": concentration,
        "related_query_breadth": breadth,
        "related_query_intensity": intensity,
        "qoq_growth": _qoq_growth(brand),
        "yoy_seasonal": _yoy_seasonal(brand),
        "festival_adjusted_change": _festival_adjusted_change(brand),
        "pre_earn_7d": _momentum(7),
        "pre_earn_14d": _momentum(14),
        "pre_earn_21d": _momentum(21),
        "pre_earn_30d": _momentum(30),
        "brand_last": float(brand.iloc[-1]) if len(brand) else None,
        "tx_last": float(tx.iloc[-1]) if len(tx) else None,
        "risk_last": float(risk.iloc[-1]) if len(risk) else None,
        "sparsity": sparse,
    }

    # Cross-signal fixture adapters (live feeds plug in with same schema)
    try:
        from quant_os_api.trends.cross_signals import load_cross_signals

        xs = load_cross_signals(entity_id, window=window, as_of=as_of)
        m = xs.get("metrics") or {}
        features["corr_app_rank"] = m.get("corr_app_rank")
        features["corr_satellite"] = m.get("corr_satellite")
        features["corr_pricing_promo"] = m.get("corr_pricing_promo")
        features["corr_hiring"] = m.get("corr_hiring")
        features["divergence_satellite"] = m.get("divergence_satellite")
        features["divergence_app_rank"] = m.get("divergence_app_rank")
        features["divergence_pricing"] = m.get("divergence_pricing")
        features["divergence_hiring"] = m.get("divergence_hiring")
        features["search_confirmation_composite"] = xs.get("search_confirmation_composite")
        cross_panel = xs
    except Exception:  # noqa: BLE001 — features must not fail closed on alt-data
        features["corr_app_rank"] = None
        features["corr_satellite"] = None
        features["corr_pricing_promo"] = None
        features["corr_hiring"] = None
        features["divergence_satellite"] = None
        features["divergence_app_rank"] = None
        features["divergence_pricing"] = None
        features["divergence_hiring"] = None
        features["search_confirmation_composite"] = None
        cross_panel = None

    # Series for charts (last 40 points)
    chart = {
        "brand": [
            {"date": str(i.date()), "interest": float(v)}
            for i, v in list(brand.iloc[-40:].items())
        ],
        "transactional": [
            {"date": str(i.date()), "interest": float(v)}
            for i, v in list(tx.iloc[-40:].items())
        ],
    }

    # Regional latest for heatmap
    heatmap: list[dict[str, Any]] = []
    if not regions.empty:
        latest = regions[regions["run_id"] == regions["run_id"].max()]
        by_reg = latest.groupby("region")["interest"].mean().sort_values(ascending=False)
        heatmap = [{"region": str(k), "interest": round(float(v), 2)} for k, v in by_reg.items()]

    rising_feed: list[dict[str, Any]] = []
    if not related.empty:
        r = related[related["mode"] == "rising"].sort_values("value", ascending=False).head(12)
        rising_feed = [
            {
                "query": str(row["related_query"]),
                "value": float(row["value"]),
                "window": str(row.get("window", "")),
            }
            for _, row in r.iterrows()
        ]

    payload = {
        "entity_id": entity_id,
        "label": cfg.get("label", entity_id),
        "ticker": cfg.get("ticker"),
        "as_of": as_of,
        "window": window,
        "ok": True,
        "is_absolute_volume": False,
        "features": features,
        "chart": chart,
        "heatmap": heatmap,
        "rising_queries": rising_feed,
        "cross_signal": cross_panel,
        "feature_attribution_note": "All interest features are relative indices within shared query groups/windows.",
    }
    trends_store.write_features(entity_id, as_of=as_of, payload=payload)
    return payload
