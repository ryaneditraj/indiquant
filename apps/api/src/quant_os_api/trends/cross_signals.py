"""Cross-signal fixture adapters — satellite, app rank, pricing/promo, hiring.

Offline-first: generates correlated / divergent series aligned to Trends brand
interest so divergence features and alerts actually compute. Replace adapters
with live feeds when those modules exist; keep the same return shape.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd

from quant_os_api.trends import store as trends_store

CHANNELS = ("satellite", "app_rank", "pricing_promo", "hiring")


def _seed(entity_id: str, channel: str) -> int:
    h = hashlib.sha256(f"cross|{entity_id}|{channel}".encode()).hexdigest()
    return int(h[:8], 16)


def _brand_series(entity_id: str, *, window: str = "90d", as_of: str | None = None) -> pd.Series:
    interest = trends_store.read_interest(entity_id, as_of=as_of)
    if interest.empty:
        return pd.Series(dtype=float)
    frame = interest[interest["window"] == window].copy()
    brand = frame[frame["query_type"] == "brand"]
    if brand.empty:
        brand = frame
    if "run_id" in brand.columns and not brand.empty:
        brand = brand[brand["run_id"] == brand["run_id"].max()]
    if brand.empty:
        return pd.Series(dtype=float)
    g = brand.groupby("date", as_index=False)["interest"].mean().sort_values("date")
    return pd.Series(g["interest"].to_numpy(dtype=float), index=pd.to_datetime(g["date"]))


def _aligned_fixture(
    brand: pd.Series,
    *,
    entity_id: str,
    channel: str,
    corr: float,
    lag: int = 0,
    shock_scale: float = 4.0,
) -> pd.Series:
    """Build a series with target correlation to brand + optional lag/shock."""
    if brand.empty:
        # Standalone synthetic when Trends not collected yet
        rng = np.random.default_rng(_seed(entity_id, channel))
        n = 40
        end = datetime.now(UTC).date()
        dates = [end - timedelta(days=i) for i in range(n)][::-1]
        vals = 50 + rng.normal(0, 8, size=n).cumsum() * 0.05
        return pd.Series(np.clip(vals, 0, 100), index=pd.to_datetime(dates))

    rng = np.random.default_rng(_seed(entity_id, channel))
    y = brand.to_numpy(dtype=float)
    noise = rng.normal(0, shock_scale, size=len(y))
    # Mix correlated component with orthogonal noise
    mu, sigma = float(y.mean()), float(y.std() or 1.0)
    z = (y - mu) / sigma
    ortho = rng.normal(0, 1, size=len(y))
    ortho = ortho - np.dot(ortho, z) / (np.dot(z, z) + 1e-9) * z
    mixed = corr * z + np.sqrt(max(0.0, 1.0 - corr**2)) * ortho
    out = mu + sigma * mixed + noise * 0.25
    if lag > 0 and len(out) > lag:
        out = np.concatenate([out[:lag], out[:-lag]])
    # Channel-specific scale quirks (still relative 0–100-like indices)
    if channel == "app_rank":
        # Invert: lower rank = better; store as inverted rank score 0–100
        out = 100.0 - np.clip((out - out.min()) / (np.ptp(out) + 1e-9) * 40 + 20, 0, 100)
    else:
        out = np.clip(out, 0, 100)
    return pd.Series(out, index=brand.index)


def load_cross_signals(
    entity_id: str,
    *,
    window: str = "90d",
    as_of: str | None = None,
) -> dict[str, Any]:
    """Return fixture (or future live) cross-signal series + summary metrics."""
    brand = _brand_series(entity_id, window=window, as_of=as_of)

    # Designed relationships:
    # satellite ~ strong positive corr; app_rank moderate; pricing mild lag;
    # hiring weaker / sometimes divergent
    specs = {
        "satellite": {"corr": 0.72, "lag": 0, "shock_scale": 3.0},
        "app_rank": {"corr": 0.55, "lag": 1, "shock_scale": 5.0},
        "pricing_promo": {"corr": 0.35, "lag": 2, "shock_scale": 6.0},
        "hiring": {"corr": 0.15, "lag": 0, "shock_scale": 8.0},
    }
    # Inject controlled divergence for some entities so alerts fire
    diverge = hashlib.sha256(entity_id.encode()).hexdigest()[0] in "89abcdef"
    if diverge:
        specs["satellite"]["corr"] = -0.35
        specs["hiring"]["corr"] = 0.8

    series: dict[str, pd.Series] = {}
    for ch, sp in specs.items():
        series[ch] = _aligned_fixture(brand, entity_id=entity_id, channel=ch, **sp)

    def _corr(a: pd.Series, b: pd.Series) -> float | None:
        if len(a) < 8 or len(b) < 8:
            return None
        joined = pd.concat([a.rename("a"), b.rename("b")], axis=1).dropna()
        if len(joined) < 8:
            return None
        return float(joined["a"].corr(joined["b"]))

    def _divergence(a: pd.Series, b: pd.Series) -> float | None:
        """Recent growth gap (search minus other) — positive => search leading up."""
        if len(a) < 14 or len(b) < 14:
            return None
        ag = float(a.iloc[-1] - a.iloc[-14]) / max(abs(float(a.iloc[-14])), 1.0)
        bg = float(b.iloc[-1] - b.iloc[-14]) / max(abs(float(b.iloc[-14])), 1.0)
        return ag - bg

    metrics = {
        "corr_satellite": _corr(brand, series["satellite"]),
        "corr_app_rank": _corr(brand, series["app_rank"]),
        "corr_pricing_promo": _corr(brand, series["pricing_promo"]),
        "corr_hiring": _corr(brand, series["hiring"]),
        "divergence_satellite": _divergence(brand, series["satellite"]),
        "divergence_app_rank": _divergence(brand, series["app_rank"]),
        "divergence_pricing": _divergence(brand, series["pricing_promo"]),
        "divergence_hiring": _divergence(brand, series["hiring"]),
    }

    def _chart(s: pd.Series, n: int = 40) -> list[dict[str, Any]]:
        return [
            {"date": str(i.date()), "value": round(float(v), 2)}
            for i, v in list(s.iloc[-n:].items())
        ]

    panel = {
        "satellite": {
            "label": "Satellite parking",
            "source": "fixture",
            "corr_with_search": metrics["corr_satellite"],
            "divergence": metrics["divergence_satellite"],
            "latest": float(series["satellite"].iloc[-1]) if len(series["satellite"]) else None,
            "series": _chart(series["satellite"]),
        },
        "app_rank": {
            "label": "App rank / reviews",
            "source": "fixture",
            "corr_with_search": metrics["corr_app_rank"],
            "divergence": metrics["divergence_app_rank"],
            "latest": float(series["app_rank"].iloc[-1]) if len(series["app_rank"]) else None,
            "series": _chart(series["app_rank"]),
        },
        "pricing_promo": {
            "label": "Pricing / promo",
            "source": "fixture",
            "corr_with_search": metrics["corr_pricing_promo"],
            "divergence": metrics["divergence_pricing"],
            "latest": float(series["pricing_promo"].iloc[-1]) if len(series["pricing_promo"]) else None,
            "series": _chart(series["pricing_promo"]),
        },
        "hiring": {
            "label": "Hiring",
            "source": "fixture",
            "corr_with_search": metrics["corr_hiring"],
            "divergence": metrics["divergence_hiring"],
            "latest": float(series["hiring"].iloc[-1]) if len(series["hiring"]) else None,
            "series": _chart(series["hiring"]),
        },
    }

    # Confirmation composite: average of abs(corr) with sign agreement on momentum
    corrs = [metrics[k] for k in ("corr_satellite", "corr_app_rank", "corr_pricing_promo") if metrics[k] is not None]
    confirmation = float(np.mean([max(0.0, c) for c in corrs])) if corrs else None

    return {
        "entity_id": entity_id,
        "window": window,
        "as_of": as_of or datetime.now(UTC).date().isoformat(),
        "source": "fixture",
        "note": "Fixture adapters generate correlated/divergent series offline. Swap for live feeds when available — same schema.",
        "is_absolute_volume": False,
        "metrics": metrics,
        "search_confirmation_composite": confirmation,
        "panel": panel,
        "brand_series": _chart(brand) if len(brand) else [],
    }
