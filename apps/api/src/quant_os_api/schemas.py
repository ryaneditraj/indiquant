"""Pydantic request/response schemas."""

from __future__ import annotations

from datetime import date, datetime
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


class HypothesisCreate(BaseModel):
    title: str
    thesis: str
    rationale: str = ""
    family: str = "unspecified"
    tags: list[str] = Field(default_factory=list)


class HypothesisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    thesis: str
    rationale: str
    family: str
    tags: list[Any]
    created_at: datetime
    updated_at: datetime


class StrategyCreate(BaseModel):
    name: str
    idea: str = ""
    logic_summary: str = ""
    code: str = ""
    hypothesis_id: UUID | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    regimes: list[Any] = Field(default_factory=list)
    weaknesses: str = ""
    improvements: str = ""
    ai_notes: str = ""


class StrategyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    hypothesis_id: UUID | None
    name: str
    idea: str
    logic_summary: str
    code: str
    version: int
    weaknesses: str
    improvements: str
    ai_notes: str
    parameters: dict[str, Any]
    regimes: list[Any]
    created_at: datetime
    updated_at: datetime


class ExperimentCreate(BaseModel):
    strategy_id: UUID | None = None
    status: str = "queued"
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)
    reasoning: str = ""
    ai_summary: str = ""
    rejection_reason: str = ""
    tags: list[str] = Field(default_factory=list)
    dependencies: list[Any] = Field(default_factory=list)
    reproducibility_score: float = 0.0
    confidence: float = 0.0


class ExperimentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    strategy_id: UUID | None
    status: str
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    metrics: dict[str, Any]
    reasoning: str
    ai_summary: str
    rejection_reason: str
    tags: list[Any]
    dependencies: list[Any]
    reproducibility_score: float
    confidence: float
    created_at: datetime
    updated_at: datetime


class IngestRequest(BaseModel):
    symbol: str
    start: date
    end: date
    timeframe: str = "1d"
    provider: str | None = None


class ResearchCycleRequest(BaseModel):
    symbol: str = "RELIANCE"
    lookback_days: int = 365
    seed: int = 42
    provider: str | None = None
    persist: bool = True


class BacktestRequest(BaseModel):
    symbol: str
    family: str = "momentum"
    provider: str | None = None
    start: date | None = None
    end: date | None = None
    persist: bool = True


class ChatRequest(BaseModel):
    messages: list[dict[str, str]]
    experiment_ids: list[str] = Field(default_factory=list)


class PortfolioRequest(BaseModel):
    symbols: list[str] = Field(default_factory=lambda: ["RELIANCE", "TCS", "INFY"])


class LoopControlRequest(BaseModel):
    symbols: list[str] = Field(default_factory=lambda: ["RELIANCE", "TCS", "INFY"])
    provider: str | None = "fixture"
    interval_seconds: float = 2.0
    max_cycles: int | None = 5


class NotebookExecuteRequest(BaseModel):
    code: str


class DuckDBQueryRequest(BaseModel):
    sql: str
    max_rows: int = 200


class EncryptRequest(BaseModel):
    value: str


class TrendsCollectRequest(BaseModel):
    entity_id: str = "dmart"
    provider: str | None = None
    windows: list[str] | None = None


class TrendsScoreRequest(BaseModel):
    entity_id: str = "dmart"
    as_of: str | None = None
    window: str = "90d"


class TrendsTrainRequest(BaseModel):
    entity_id: str | None = None
    entity_ids: list[str] | None = None


class TrendsPredictRequest(BaseModel):
    entity_id: str = "dmart"
    as_of: str | None = None
    window: str = "90d"


class TrendsRankRequest(BaseModel):
    entity_ids: list[str] | None = None
    window: str = "90d"
