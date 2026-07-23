"""Portfolio lab — correlation, risk contribution, simple efficient frontier."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def correlation_matrix(returns: pd.DataFrame) -> dict[str, Any]:
    corr = returns.corr().fillna(0.0)
    return {
        "symbols": list(corr.columns),
        "matrix": corr.round(4).values.tolist(),
    }


def risk_contribution(weights: np.ndarray, cov: np.ndarray) -> list[float]:
    port_var = float(weights.T @ cov @ weights)
    if port_var <= 1e-18:
        return [0.0] * len(weights)
    mrc = cov @ weights
    rc = weights * mrc / port_var
    return [float(x) for x in rc]


def efficient_frontier(
    returns: pd.DataFrame,
    *,
    n_portfolios: int = 500,
    seed: int = 7,
) -> dict[str, Any]:
    if returns.shape[1] < 2 or len(returns) < 10:
        return {"points": [], "reason": "need >=2 series and >=10 rows"}
    rng = np.random.default_rng(seed)
    mu = returns.mean().to_numpy() * 252
    cov = returns.cov().to_numpy() * 252
    n = returns.shape[1]
    points = []
    for _ in range(n_portfolios):
        w = rng.random(n)
        w /= w.sum()
        ret = float(w @ mu)
        vol = float(np.sqrt(w.T @ cov @ w))
        points.append(
            {
                "return": ret,
                "volatility": vol,
                "weights": {col: float(w[i]) for i, col in enumerate(returns.columns)},
            }
        )
    points.sort(key=lambda p: p["volatility"])
    return {"points": points[:: max(len(points) // 40, 1)], "n": len(points)}


def portfolio_report(equity_curves: dict[str, list[float]]) -> dict[str, Any]:
    frame = pd.DataFrame({k: pd.Series(v) for k, v in equity_curves.items()}).dropna()
    if frame.empty:
        return {"error": "empty equity curves"}
    rets = frame.pct_change().dropna()
    equal = np.repeat(1 / rets.shape[1], rets.shape[1])
    cov = rets.cov().to_numpy() * 252
    return {
        "correlation": correlation_matrix(rets),
        "equal_weight_risk_contribution": dict(
            zip(rets.columns, risk_contribution(equal, cov), strict=True)
        ),
        "frontier": efficient_frontier(rets),
    }
