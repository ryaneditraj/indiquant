"""In-process forever research loop with pause / resume / stop."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from quant_os_api.db import get_session_factory
from quant_os_api.services.ai_loop import run_research_cycle
from quant_os_api.services.audit import write_audit
from quant_os_api.services.persistence import persist_loop_result


@dataclass
class LoopState:
    loop_id: str
    status: str = "idle"  # idle | running | paused | stopped
    symbols: list[str] = field(default_factory=lambda: ["RELIANCE", "TCS", "INFY"])
    provider: str | None = "fixture"
    interval_seconds: float = 2.0
    max_cycles: int | None = None
    cycles_completed: int = 0
    accepted: int = 0
    rejected: int = 0
    last_error: str = ""
    last_experiment_id: str = ""
    started_at: str | None = None
    updated_at: str | None = None
    history: list[dict[str, Any]] = field(default_factory=list)


class ResearchLoopController:
    """Thread-backed research loop — Celery can call the same cycle function."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._pause = threading.Event()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.state = LoopState(loop_id=str(uuid4()))
        self._pause.set()  # not paused initially when idle

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "loop_id": self.state.loop_id,
                "status": self.state.status,
                "symbols": list(self.state.symbols),
                "provider": self.state.provider,
                "interval_seconds": self.state.interval_seconds,
                "max_cycles": self.state.max_cycles,
                "cycles_completed": self.state.cycles_completed,
                "accepted": self.state.accepted,
                "rejected": self.state.rejected,
                "last_error": self.state.last_error,
                "last_experiment_id": self.state.last_experiment_id,
                "started_at": self.state.started_at,
                "updated_at": self.state.updated_at,
                "history": list(self.state.history[-20:]),
            }

    def start(
        self,
        *,
        symbols: list[str] | None = None,
        provider: str | None = "fixture",
        interval_seconds: float = 2.0,
        max_cycles: int | None = 5,
    ) -> dict[str, Any]:
        with self._lock:
            if self.state.status == "running":
                return self.snapshot()
            self._stop.clear()
            self._pause.set()
            self.state = LoopState(
                loop_id=str(uuid4()),
                status="running",
                symbols=symbols or ["RELIANCE", "TCS", "INFY"],
                provider=provider,
                interval_seconds=max(0.5, interval_seconds),
                max_cycles=max_cycles,
                started_at=datetime.now(UTC).isoformat(),
                updated_at=datetime.now(UTC).isoformat(),
            )
            self._thread = threading.Thread(target=self._run, name="research-loop", daemon=True)
            self._thread.start()
            write_audit("research_loop_started", details=self.snapshot())
            return self.snapshot()

    def pause(self) -> dict[str, Any]:
        with self._lock:
            if self.state.status != "running":
                return self.snapshot()
            self._pause.clear()
            self.state.status = "paused"
            self.state.updated_at = datetime.now(UTC).isoformat()
            write_audit("research_loop_paused", details={"loop_id": self.state.loop_id})
            return self.snapshot()

    def resume(self) -> dict[str, Any]:
        with self._lock:
            if self.state.status != "paused":
                return self.snapshot()
            self._pause.set()
            self.state.status = "running"
            self.state.updated_at = datetime.now(UTC).isoformat()
            write_audit("research_loop_resumed", details={"loop_id": self.state.loop_id})
            return self.snapshot()

    def stop(self) -> dict[str, Any]:
        with self._lock:
            self._stop.set()
            self._pause.set()
            self.state.status = "stopped"
            self.state.updated_at = datetime.now(UTC).isoformat()
            write_audit("research_loop_stopped", details={"loop_id": self.state.loop_id})
            return self.snapshot()

    def _run(self) -> None:
        idx = 0
        while not self._stop.is_set():
            self._pause.wait()
            if self._stop.is_set():
                break
            with self._lock:
                if self.state.max_cycles is not None and self.state.cycles_completed >= self.state.max_cycles:
                    self.state.status = "stopped"
                    self.state.updated_at = datetime.now(UTC).isoformat()
                    write_audit("research_loop_completed", details=self.snapshot())
                    break
                symbols = list(self.state.symbols)
                provider = self.state.provider
                seed = self.state.cycles_completed + 1
                interval = self.state.interval_seconds

            symbol = symbols[idx % len(symbols)]
            idx += 1
            try:
                result = run_research_cycle(symbol=symbol, seed=seed, provider_name=provider)
                SessionLocal = get_session_factory()
                db = SessionLocal()
                try:
                    persisted = persist_loop_result(db, result)
                finally:
                    db.close()
                with self._lock:
                    self.state.cycles_completed += 1
                    if result.accepted:
                        self.state.accepted += 1
                    else:
                        self.state.rejected += 1
                    self.state.last_experiment_id = persisted["experiment_id"]
                    self.state.last_error = ""
                    self.state.updated_at = datetime.now(UTC).isoformat()
                    self.state.history.append(
                        {
                            "symbol": symbol,
                            "accepted": result.accepted,
                            "experiment_id": persisted["experiment_id"],
                            "summary": result.experiment.get("ai_summary", "")[:160],
                        }
                    )
            except Exception as exc:  # noqa: BLE001
                with self._lock:
                    self.state.last_error = str(exc)
                    self.state.updated_at = datetime.now(UTC).isoformat()
                    self.state.cycles_completed += 1
            time.sleep(interval)

        with self._lock:
            if self.state.status == "running":
                self.state.status = "stopped"
                self.state.updated_at = datetime.now(UTC).isoformat()


_controller: ResearchLoopController | None = None
_controller_lock = threading.Lock()


def get_loop_controller() -> ResearchLoopController:
    global _controller
    with _controller_lock:
        if _controller is None:
            _controller = ResearchLoopController()
        return _controller


def reset_loop_controller() -> ResearchLoopController:
    """Test helper — stop and replace the singleton."""
    global _controller
    with _controller_lock:
        if _controller is not None:
            _controller.stop()
        _controller = ResearchLoopController()
        return _controller
