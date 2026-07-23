"""Corporate actions stub — plug real calendars via config later."""

from __future__ import annotations

from datetime import date
from typing import Any


def list_corporate_actions(symbol: str, start: date, end: date) -> list[dict[str, Any]]:
    """Return empty list until a corporate-actions provider is configured."""
    return []


def adjust_for_splits(bars: list[dict[str, Any]], actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Identity adjust — placeholder for split/dividend normalization."""
    _ = actions
    return bars
