"""Audit log — append-only JSONL under artifacts/audit."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from quant_os_api.config import _repo_root, get_settings


def audit_path() -> Path:
    settings = get_settings()
    root = settings.yaml_config.get("storage", {}).get("artifacts_root", "artifacts")
    path = Path(str(root))
    if not path.is_absolute():
        path = _repo_root() / path
    path = path / "audit"
    path.mkdir(parents=True, exist_ok=True)
    return path / "audit.jsonl"


def write_audit(event: str, *, actor: str = "system", details: dict[str, Any] | None = None) -> dict[str, Any]:
    record = {
        "id": str(uuid4()),
        "ts": datetime.now(UTC).isoformat(),
        "event": event,
        "actor": actor,
        "details": details or {},
    }
    path = audit_path()
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, default=str) + "\n")
    return record


def read_audit(*, limit: int = 100) -> list[dict[str, Any]]:
    path = audit_path()
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    records = [json.loads(line) for line in lines if line.strip()]
    return list(reversed(records[-limit:]))
