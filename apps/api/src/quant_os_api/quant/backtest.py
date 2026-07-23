"""Bar backtest engine — long/flat, fees + slippage in bps, configurable cash."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np
import pandas as pd

from quant_os_api.quant.metrics import compute_metrics

Signal = Literal[-1, 0, 1]


@dataclass
class BacktestConfig:
    initial_cash: float = 1_000_000.0
    fee_bps: float = 3.0
    slippage_bps: float = 2.0
    position_size: float = 1.0  # fraction of equity


@dataclass
class BacktestResult:
    equity_curve: list[dict[str, Any]] = field(default_factory=list)
    trades: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    signals_used: int = 0


def sma_crossover_signals(close: pd.Series, fast: int = 10, slow: int = 30) -> pd.Series:
    """Example strategy family: momentum via SMA crossover. Hypothesis-first demo."""
    fast_ma = close.rolling(fast).mean()
    slow_ma = close.rolling(slow).mean()
    signal = pd.Series(0, index=close.index, dtype=int)
    signal = signal.mask(fast_ma > slow_ma, 1)
    # Shift by 1 to avoid lookahead — trade next bar open/close
    return signal.shift(1).fillna(0).astype(int)


def run_bar_backtest(
    bars: pd.DataFrame,
    signals: pd.Series,
    config: BacktestConfig | None = None,
) -> BacktestResult:
    cfg = config or BacktestConfig()
    if bars.empty:
        return BacktestResult(metrics=compute_metrics(pd.Series(dtype=float)))

    frame = bars.copy()
    if "close" not in frame.columns:
        raise ValueError("bars require close column")
    frame = frame.reset_index(drop=True)
    signals = signals.reindex(frame.index).fillna(0).astype(int)

    cash = cfg.initial_cash
    shares = 0.0
    equity_rows: list[dict[str, Any]] = []
    trades: list[dict[str, Any]] = []
    cost_rate = (cfg.fee_bps + cfg.slippage_bps) / 10_000.0

    for i, row in frame.iterrows():
        price = float(row["close"])
        target = int(signals.iloc[i])
        desired_shares = (cash + shares * price) * cfg.position_size / price if target > 0 else 0.0
        delta = desired_shares - shares
        if abs(delta) > 1e-9:
            notional = abs(delta) * price
            cost = notional * cost_rate
            cash -= delta * price + cost
            shares += delta
            trades.append(
                {
                    "i": int(i),
                    "ts": str(row.get("ts", i)),
                    "side": "buy" if delta > 0 else "sell",
                    "shares": abs(delta),
                    "price": price,
                    "cost": cost,
                }
            )
        equity = cash + shares * price
        equity_rows.append({"ts": str(row.get("ts", i)), "equity": equity})

    equity_series = pd.Series([r["equity"] for r in equity_rows], dtype=float)
    return BacktestResult(
        equity_curve=equity_rows,
        trades=trades,
        metrics=compute_metrics(equity_series),
        signals_used=int((signals != 0).sum()),
    )


def mean_reversion_signals(close: pd.Series, lookback: int = 20, z: float = 1.0) -> pd.Series:
    """Mean-reversion demo: long when z-score below -z."""
    mu = close.rolling(lookback).mean()
    sigma = close.rolling(lookback).std()
    score = (close - mu) / sigma.replace(0, np.nan)
    signal = pd.Series(0, index=close.index, dtype=int)
    signal = signal.mask(score < -z, 1)
    return signal.shift(1).fillna(0).astype(int)
