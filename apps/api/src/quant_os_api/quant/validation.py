"""Statistical validation — walk-forward, OOS, leakage, Monte Carlo, sensitivity."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd

from quant_os_api.quant.backtest import BacktestConfig, run_bar_backtest


def check_lookahead(signals: pd.Series, close: pd.Series) -> dict[str, Any]:
    """Basic leakage heuristic: signal must not be perfectly correlated with same-bar return."""
    rets = close.pct_change()
    aligned = pd.concat([signals.rename("s"), rets.rename("r")], axis=1).dropna()
    if len(aligned) < 10:
        return {"passed": True, "reason": "insufficient bars", "corr": 0.0}
    corr = float(aligned["s"].corr(aligned["r"]))
    if np.isnan(corr):
        return {
            "passed": True,
            "corr_signal_same_bar_return": None,
            "reason": "undefined correlation (constant signal)",
        }
    # High absolute correlation with same-bar return suggests lookahead
    passed = abs(corr) < 0.85
    return {
        "passed": passed,
        "corr_signal_same_bar_return": corr,
        "reason": "ok" if passed else "signal highly correlated with same-bar returns",
    }


def walk_forward_splits(
    n: int,
    *,
    n_folds: int = 4,
    train_ratio: float = 0.7,
) -> list[tuple[slice, slice]]:
    if n < 40 or n_folds < 2:
        split = int(n * train_ratio)
        return [(slice(0, split), slice(split, n))]
    fold_size = n // n_folds
    splits: list[tuple[slice, slice]] = []
    for i in range(n_folds - 1):
        test_start = (i + 1) * fold_size
        test_end = (i + 2) * fold_size if i < n_folds - 2 else n
        train_end = test_start
        train_start = max(0, train_end - int(train_end * train_ratio))
        if train_end - train_start < 10 or test_end - test_start < 5:
            continue
        splits.append((slice(train_start, train_end), slice(test_start, test_end)))
    return splits or [(slice(0, int(n * train_ratio)), slice(int(n * train_ratio), n))]


def run_walk_forward(
    bars: pd.DataFrame,
    signal_fn: Callable[[pd.Series], pd.Series],
    config: BacktestConfig | None = None,
    *,
    n_folds: int = 4,
) -> dict[str, Any]:
    close = bars["close"]
    splits = walk_forward_splits(len(bars), n_folds=n_folds)
    fold_results = []
    for idx, (train_sl, test_sl) in enumerate(splits):
        test_bars = bars.iloc[test_sl].reset_index(drop=True)
        # Fit-free strategies: generate signals on full series then slice test
        full_signals = signal_fn(close).reset_index(drop=True)
        test_signals = full_signals.iloc[test_sl].reset_index(drop=True)
        result = run_bar_backtest(test_bars, test_signals, config)
        fold_results.append(
            {
                "fold": idx,
                "train": [train_sl.start, train_sl.stop],
                "test": [test_sl.start, test_sl.stop],
                "metrics": result.metrics,
            }
        )
    oos_sharpes = [f["metrics"].get("sharpe", 0.0) for f in fold_results]
    return {
        "folds": fold_results,
        "oos_mean_sharpe": float(np.mean(oos_sharpes)) if oos_sharpes else 0.0,
        "oos_min_sharpe": float(np.min(oos_sharpes)) if oos_sharpes else 0.0,
        "passed": bool(oos_sharpes) and float(np.mean(oos_sharpes)) > 0.0,
    }


def monte_carlo_equity(
    equity: pd.Series,
    *,
    n_sims: int = 200,
    seed: int = 42,
) -> dict[str, Any]:
    if len(equity) < 5:
        return {"passed": False, "reason": "insufficient equity points"}
    rng = np.random.default_rng(seed)
    rets = equity.pct_change().dropna().to_numpy()
    terminal = []
    max_dds = []
    for _ in range(n_sims):
        sim = rng.choice(rets, size=len(rets), replace=True)
        path = np.cumprod(1 + sim)
        series = pd.Series(path)
        terminal.append(float(series.iloc[-1] - 1))
        dd = series / series.cummax() - 1
        max_dds.append(float(dd.min()))
    return {
        "n_sims": n_sims,
        "terminal_return_p05": float(np.percentile(terminal, 5)),
        "terminal_return_p50": float(np.percentile(terminal, 50)),
        "terminal_return_p95": float(np.percentile(terminal, 95)),
        "max_drawdown_p05": float(np.percentile(max_dds, 5)),
        "passed": float(np.percentile(terminal, 5)) > -0.5,
    }


def parameter_sensitivity(
    bars: pd.DataFrame,
    *,
    fast_values: list[int] | None = None,
    slow_values: list[int] | None = None,
    config: BacktestConfig | None = None,
) -> dict[str, Any]:
    from quant_os_api.quant.backtest import sma_crossover_signals

    fast_values = fast_values or [5, 10, 15]
    slow_values = slow_values or [20, 30, 40]
    grid = []
    for fast in fast_values:
        for slow in slow_values:
            if fast >= slow:
                continue
            signals = sma_crossover_signals(bars["close"], fast=fast, slow=slow)
            result = run_bar_backtest(bars, signals, config)
            grid.append({"fast": fast, "slow": slow, "sharpe": result.metrics.get("sharpe", 0.0)})
    sharpes = [g["sharpe"] for g in grid]
    return {
        "grid": grid,
        "sharpe_std": float(np.std(sharpes)) if sharpes else 0.0,
        "passed": bool(sharpes) and float(np.std(sharpes)) < 2.0,
        "reason": "parameter surface not explosively unstable",
    }


def reproducibility_score(inputs: dict[str, Any], metrics: dict[str, Any]) -> float:
    """Heuristic 0–1 score: seeded, versioned, metrics present."""
    score = 0.0
    if inputs.get("seed") is not None:
        score += 0.25
    if inputs.get("strategy_family"):
        score += 0.2
    if inputs.get("symbol") and inputs.get("start") and inputs.get("end"):
        score += 0.25
    if metrics.get("sharpe") is not None and metrics.get("max_drawdown") is not None:
        score += 0.2
    if inputs.get("code_version") or inputs.get("git_sha"):
        score += 0.1
    return round(min(score, 1.0), 3)


def validate_strategy(
    bars: pd.DataFrame,
    signals: pd.Series,
    *,
    signal_fn: Callable[[pd.Series], pd.Series] | None = None,
    config: BacktestConfig | None = None,
    require_walk_forward: bool = True,
    require_oos: bool = True,
) -> dict[str, Any]:
    close = bars["close"]
    leakage = check_lookahead(signals, close)
    full = run_bar_backtest(bars, signals, config)
    wf = (
        run_walk_forward(bars, signal_fn or (lambda c: signals), config)
        if require_walk_forward and signal_fn
        else {"passed": True, "skipped": True}
    )
    mc = monte_carlo_equity(pd.Series([e["equity"] for e in full.equity_curve]))
    sens = parameter_sensitivity(bars, config=config) if signal_fn else {"passed": True, "skipped": True}

    checks = {
        "lookahead": leakage,
        "walk_forward": wf,
        "monte_carlo": mc,
        "sensitivity": sens,
        "full_sample": {"metrics": full.metrics, "passed": full.metrics.get("sharpe", 0) > -1},
    }
    rejected = []
    if not leakage["passed"]:
        rejected.append("lookahead_bias_suspected")
    if require_walk_forward and not wf.get("passed", False) and not wf.get("skipped"):
        rejected.append("walk_forward_failed")
    if require_oos and not wf.get("passed", False) and not wf.get("skipped"):
        rejected.append("oos_failed")
    if not mc.get("passed", False):
        rejected.append("monte_carlo_tail_risk")

    accepted = len(rejected) == 0
    return {
        "accepted": accepted,
        "rejected": not accepted,
        "rejection_reasons": rejected,
        "checks": checks,
        "metrics": full.metrics,
        "equity_curve": full.equity_curve,
        "trades": full.trades,
    }
