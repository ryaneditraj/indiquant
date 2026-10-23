"""DuckDB analytics over Parquet OHLCV."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from quant_os_api.config import _repo_root, get_settings
from quant_os_api.safe_ids import safe_symbol, safe_timeframe
from quant_os_api.services import parquet_store

# Table functions and statements that can read arbitrary files or mutate state.
_BLOCKED_SQL = re.compile(
    r"\b("
    r"read_[a-z0-9_]*|parquet_scan|glob|iceberg_scan|delta_scan|"
    r"sqlite_scan|postgres_scan|mysql_scan|attach|copy|export|import|"
    r"install|load|pragma|call"
    r")\b"
)


def duckdb_path() -> Path:
    settings = get_settings()
    raw = settings.yaml_config.get("duckdb", {}).get("path", "data/analytics/quant_os.duckdb")
    path = Path(str(raw))
    if not path.is_absolute():
        path = _repo_root() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def sync_parquet_to_duckdb() -> dict[str, Any]:
    """Register / refresh parquet files into DuckDB views."""
    try:
        import duckdb
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("duckdb package not installed") from exc

    datasets = parquet_store.list_datasets()
    con = duckdb.connect(str(duckdb_path()))
    registered = []
    try:
        for ds in datasets:
            symbol = safe_symbol(str(ds["symbol"]))
            timeframe = safe_timeframe(str(ds["timeframe"]))
            path = parquet_store.symbol_path(symbol, timeframe)
            view = f"ohlcv_{symbol.lower()}_{timeframe}"
            # CREATE VIEW cannot take a prepared parameter in DuckDB. The path is
            # already confined to the parquet root; quotes are escaped anyway.
            escaped = str(path).replace("'", "''")
            con.execute(
                f"CREATE OR REPLACE VIEW \"{view}\" AS SELECT * FROM read_parquet('{escaped}')"
            )
            registered.append(view)
        summary = con.execute(
            """
            SELECT ? AS dataset_count, ? AS duckdb_path
            """,
            [len(registered), str(duckdb_path())],
        ).fetchone()
    finally:
        con.close()
    return {
        "registered_views": registered,
        "dataset_count": int(summary[0]) if summary else len(registered),
        "path": str(duckdb_path()),
    }


def query_duckdb(sql: str, *, max_rows: int = 500) -> dict[str, Any]:
    """Run read-only analytics SQL. Only a single SELECT is allowed."""
    stripped = sql.strip().lower()
    if not stripped.startswith("select"):
        raise ValueError("Only SELECT queries are allowed")
    # Reject stacked statements and comment tricks (`SELECT 1; DROP …`).
    if ";" in stripped.rstrip(";"):
        raise ValueError("Only a single SELECT statement is allowed")
    if "--" in stripped or "/*" in stripped:
        raise ValueError("SQL comments are not allowed")
    if re.search(r"\bfrom\s+['\"]", stripped):
        raise ValueError("Query registered views. Direct file reads are not allowed")
    if _BLOCKED_SQL.search(stripped):
        raise ValueError("File-reading and administrative SQL is not allowed")
    forbidden = ("insert", "update", "delete", "drop", "alter", "attach", "copy", "pragma", "call")
    padded = f" {stripped} "
    if any(f" {token} " in padded or f" {token}(" in padded for token in forbidden):
        raise ValueError("Mutating SQL is not allowed")

    import duckdb

    con = duckdb.connect(str(duckdb_path()), read_only=True)
    try:
        frame = con.execute(sql).fetchdf()
    finally:
        con.close()
    if len(frame) > max_rows:
        frame = frame.head(max_rows)
    return {
        "columns": list(frame.columns),
        "rows": frame.to_dict(orient="records"),
        "n": len(frame),
    }
