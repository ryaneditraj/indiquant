"""Broker plugins (paper execution first — research OS, not live trading product)."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Broker(Protocol):
    name: str

    def health(self) -> dict[str, Any]:
        ...


class PaperBroker:
    name = "paper"

    def health(self) -> dict[str, Any]:
        return {"provider": self.name, "status": "ok", "live": False}
