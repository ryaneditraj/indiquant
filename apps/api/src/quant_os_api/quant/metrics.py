"""Performance metrics for research experiments."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def compute_metrics(equity: pd.Series, *, periods_per_year: int = 252) -> dict[str, Any]:
    if equity.empty or len(equity) < 2:
        return {
            "total_return": 0.0,
            "cagr": 0.0,
            "volatility": 0.0,
            "sharpe": 0.0,
            "max_drawdown": 0.0,
            "calmar": 0.0,
            "n_bars": int(len(equity)),
        }

    returns = equity.pct_change().dropna()
    total_return = float(equity.iloc[-1] / equity.iloc[0] - 1.0)
    years = max(len(equity) / periods_per_year, 1e-9)
    cagr = float((equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1.0)
    vol = float(returns.std() * np.sqrt(periods_per_year)) if len(returns) else 0.0
    sharpe = float((returns.mean() * periods_per_year) / vol) if vol > 1e-12 else 0.0
    drawdown = equity / equity.cummax() - 1.0
    max_dd = float(drawdown.min()) if len(drawdown) else 0.0
    calmar = float(cagr / abs(max_dd)) if abs(max_dd) > 1e-12 else 0.0
    return {
        "total_return": total_return,
        "cagr": cagr,
        "volatility": vol,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "calmar": calmar,
        "n_bars": int(len(equity)),
    }
