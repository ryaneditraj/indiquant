"""Restricted notebook / REPL execution for research snippets."""

from __future__ import annotations

import contextlib
import io
import traceback
from typing import Any

ALLOWED_PREFIXES = (
    "import pandas",
    "import numpy",
    "import math",
    "from quant_os_api",
    "from datetime",
    "print(",
    "bars",
    "close",
    "signals",
    "result",
    "df",
    "x",
    "y",
    "#",
)


def execute_notebook_code(code: str, *, timeout_hint: int = 5) -> dict[str, Any]:
    """Execute a small whitelist-oriented research snippet.

    This is intentionally constrained — not a full multi-user kernel.
    Blocks obvious dangerous builtins.
    """
    _ = timeout_hint
    banned = (
        "os.system",
        "subprocess",
        "open(",
        "eval(",
        "exec(",
        "__import__",
        "Path(",
        "shutil",
        "socket",
        "requests",
        "httpx",
        "import os",
        "import sys",
    )
    lowered = code.lower()
    for token in banned:
        if token.lower() in lowered and "quant_os_api" not in token:
            if token in code or token.lower() in lowered:
                return {
                    "ok": False,
                    "error": f"Blocked token for safety: {token}",
                    "stdout": "",
                    "result": None,
                }

    # Minimal safe builtins
    safe_builtins = {
        "abs": abs,
        "min": min,
        "max": max,
        "range": range,
        "len": len,
        "print": print,
        "float": float,
        "int": int,
        "str": str,
        "list": list,
        "dict": dict,
        "round": round,
        "enumerate": enumerate,
        "zip": zip,
        "sum": sum,
        "True": True,
        "False": False,
        "None": None,
    }

    import math
    from datetime import date, datetime, timedelta

    import numpy as np
    import pandas as pd

    from quant_os_api.plugins.data.fixture import FixtureDataProvider
    from quant_os_api.quant import backtest, metrics, regimes, validation

    globals_dict: dict[str, Any] = {
        "__builtins__": safe_builtins,
        "np": np,
        "pd": pd,
        "math": math,
        "date": date,
        "datetime": datetime,
        "timedelta": timedelta,
        "FixtureDataProvider": FixtureDataProvider,
        "backtest": backtest,
        "metrics": metrics,
        "regimes": regimes,
        "validation": validation,
    }
    stdout = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout):
            exec(compile(code, "<notebook>", "exec"), globals_dict, globals_dict)  # noqa: S102
        # Prefer an explicit `result` binding
        value = globals_dict.get("result")
        if value is not None and not isinstance(value, (str, int, float, bool, list, dict)):
            value = repr(value)[:2000]
        return {"ok": True, "stdout": stdout.getvalue(), "result": value, "error": None}
    except Exception:  # noqa: BLE001
        return {
            "ok": False,
            "stdout": stdout.getvalue(),
            "result": None,
            "error": traceback.format_exc(limit=5),
        }
