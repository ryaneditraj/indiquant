"""Fundamentals label store stub.

Returns None until filings / SSS / beat-miss parquet is wired. Modeling keeps
proxy labels as fallback and exposes label_source accordingly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from quant_os_api.config import get_settings


def fundamentals_root() -> Path:
    root = Path(get_settings().yaml_config.get("paths", {}).get("data_dir", "data"))
    return root / "parquet" / "fundamentals"


def load_labels(entity_id: str, as_of: str | None = None) -> dict[str, Any] | None:
    """Load PIT fundamentals labels for an entity.

    Stub: always None (no rows). When wired, expect keys like revenue_growth,
    sss, beat_inline_miss with as_of point-in-time semantics.
    """
    _ = (entity_id, as_of, fundamentals_root())
    return None
