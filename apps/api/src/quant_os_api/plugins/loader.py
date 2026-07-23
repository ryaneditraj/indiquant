"""Dynamic plugin loader — module paths come from config.yaml only."""

from __future__ import annotations

import importlib
from typing import Any


def load_symbol(dotted_path: str) -> Any:
    """Load `package.module:ClassName` or `package.module.ClassName`."""
    if ":" in dotted_path:
        module_path, attr = dotted_path.split(":", 1)
    else:
        parts = dotted_path.rsplit(".", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid plugin path: {dotted_path}")
        module_path, attr = parts
    module = importlib.import_module(module_path)
    try:
        return getattr(module, attr)
    except AttributeError as exc:
        raise ImportError(f"Attribute {attr!r} not found in {module_path}") from exc


def instantiate_plugin(dotted_path: str, **kwargs: Any) -> Any:
    cls = load_symbol(dotted_path)
    return cls(**kwargs) if kwargs else cls()
