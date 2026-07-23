"""Pydantic schemas for API responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    env: str
    primary_market: str
    database_configured: bool
    redis_configured: bool
    features: dict[str, Any] = Field(default_factory=dict)


class SettingsPublicResponse(BaseModel):
    settings: dict[str, Any]


class DashboardSnapshot(BaseModel):
    """Placeholder live dashboard payload — filled as subsystems come online."""

    app_name: str
    research_score: float = 0.0
    ai_tasks: list[dict[str, Any]] = Field(default_factory=list)
    queued_experiments: int = 0
    completed_experiments: int = 0
    rejected_strategies: int = 0
    top_strategies: list[dict[str, Any]] = Field(default_factory=list)
    market_regime: str = "unknown"
    data_freshness: str = "unknown"
    system_health: dict[str, Any] = Field(default_factory=dict)
    recent_discoveries: list[dict[str, Any]] = Field(default_factory=list)
    timeline: list[dict[str, Any]] = Field(default_factory=list)


class ExperimentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    strategy_id: UUID | None
    reproducibility_score: float
    confidence: float
    ai_summary: str
    tags: list[Any]
    created_at: datetime
    updated_at: datetime
