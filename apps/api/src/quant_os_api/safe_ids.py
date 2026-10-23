"""Reject path and identifier tricks before they touch the filesystem or SQL."""

from __future__ import annotations

import re
from pathlib import Path

_SYMBOL = re.compile(r"^[A-Z][A-Z0-9.&-]{0,31}$")
_TIMEFRAME = re.compile(r"^[a-z0-9]{1,8}$")
_ENTITY = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_STEM = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:+-]{0,80}$")


class UnsafePathError(ValueError):
    """Caller supplied a symbol, entity, or filename that is not safe to persist."""


def safe_symbol(symbol: str) -> str:
    cleaned = symbol.strip().upper()
    if ".." in cleaned or not _SYMBOL.fullmatch(cleaned):
        raise UnsafePathError(
            "Symbol must be 1–32 characters, start with a letter, and use only "
            "letters, digits, '.', '&', or '-'."
        )
    return cleaned


def safe_timeframe(timeframe: str) -> str:
    cleaned = timeframe.strip().lower()
    if not _TIMEFRAME.fullmatch(cleaned):
        raise UnsafePathError("Timeframe must be 1–8 letters or digits, for example 1d.")
    return cleaned


def safe_entity_id(entity_id: str) -> str:
    cleaned = entity_id.strip().lower()
    if not _ENTITY.fullmatch(cleaned):
        raise UnsafePathError(
            "Entity id must start with a letter and use only lowercase letters, digits, or '_'."
        )
    return cleaned


def safe_filename_stem(value: str) -> str:
    cleaned = value.strip()
    if ".." in cleaned or "/" in cleaned or "\\" in cleaned or not _STEM.fullmatch(cleaned):
        raise UnsafePathError("Filename stem contains characters that are not allowed.")
    return cleaned


def ensure_within(root: Path, path: Path) -> Path:
    """Resolve `path` and require it to stay inside `root`."""
    root_resolved = root.resolve()
    path_resolved = path.resolve()
    if path_resolved != root_resolved and root_resolved not in path_resolved.parents:
        raise UnsafePathError("Path escapes the storage root.")
    return path_resolved
