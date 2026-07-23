"""Market regime classification — rule-based, transparent, configurable thresholds."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def classify_regimes(
    close: pd.Series,
    *,
    trend_window: int = 50,
    vol_window: int = 20,
    vol_high_percentile: float = 70.0,
    vol_low_percentile: float = 30.0,
) -> pd.DataFrame:
    rets = close.pct_change()
    trend = close.pct_change(trend_window)
    vol = rets.rolling(vol_window).std() * np.sqrt(252)
    vol_high = vol.quantile(vol_high_percentile / 100.0)
    vol_low = vol.quantile(vol_low_percentile / 100.0)

    labels = []
    for i in range(len(close)):
        t = trend.iloc[i]
        v = vol.iloc[i]
        if pd.isna(t) or pd.isna(v):
            labels.append("unknown")
            continue
        if t < -0.15 and v >= vol_high:
            labels.append("crash")
        elif t < -0.05:
            labels.append("bear")
        elif t > 0.05:
            labels.append("bull" if v < vol_high else "recovery")
        elif v >= vol_high:
            labels.append("high_volatility")
        elif v <= vol_low:
            labels.append("low_volatility")
        else:
            labels.append("sideways")

    return pd.DataFrame({"ts": close.index.astype(str), "close": close.values, "regime": labels})


def current_regime(close: pd.Series) -> dict[str, Any]:
    frame = classify_regimes(close)
    if frame.empty:
        return {"regime": "unknown", "confidence": 0.0}
    regime = str(frame["regime"].iloc[-1])
    # Confidence: stability of last N labels
    tail = frame["regime"].tail(10)
    confidence = float((tail == regime).mean()) if len(tail) else 0.0
    counts = frame["regime"].value_counts(normalize=True).to_dict()
    return {
        "regime": regime,
        "confidence": confidence,
        "distribution": {str(k): float(v) for k, v in counts.items()},
    }


def strategy_regime_performance(
    equity: pd.Series,
    regimes: pd.Series,
) -> dict[str, Any]:
    rets = equity.pct_change().fillna(0.0)
    out: dict[str, Any] = {}
    for regime in sorted(regimes.dropna().unique()):
        mask = regimes.reset_index(drop=True) == regime
        r = rets.reset_index(drop=True)[mask]
        out[str(regime)] = {
            "mean_return": float(r.mean()) if len(r) else 0.0,
            "sharpe_approx": float(r.mean() / r.std() * np.sqrt(252))
            if len(r) and r.std() > 1e-12
            else 0.0,
            "n": int(len(r)),
        }
    return out
