"""Persist research cycle outputs into SQLAlchemy models."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from quant_os_api.models import Experiment, Hypothesis, Strategy
from quant_os_api.services.ai_loop import LoopResult
from quant_os_api.services.audit import write_audit


def persist_loop_result(db: Session, result: LoopResult) -> dict[str, Any]:
    hyp = Hypothesis(
        id=uuid.UUID(result.hypothesis["id"]),
        title=result.hypothesis["title"],
        thesis=result.hypothesis["thesis"],
        rationale=result.hypothesis["rationale"],
        family=result.hypothesis["family"],
        tags=result.hypothesis.get("tags") or [],
    )
    strat = Strategy(
        id=uuid.UUID(result.strategy["id"]),
        hypothesis_id=hyp.id,
        name=result.strategy["name"],
        idea=result.strategy.get("idea", ""),
        logic_summary=result.strategy.get("logic_summary", ""),
        code=result.strategy.get("code", ""),
        parameters=result.strategy.get("parameters") or {},
        regimes=result.strategy.get("regimes") or [],
        ai_notes="; ".join(f"{e.agent}: {e.message}" for e in result.events[-5:]),
        weaknesses=result.experiment.get("rejection_reason", ""),
    )
    exp = Experiment(
        id=uuid.UUID(result.experiment["id"]),
        strategy_id=strat.id,
        status=result.experiment["status"],
        inputs=result.experiment.get("inputs") or {},
        outputs=result.experiment.get("outputs") or {},
        metrics=result.experiment.get("metrics") or {},
        reasoning=result.experiment.get("reasoning", ""),
        ai_summary=result.experiment.get("ai_summary", ""),
        rejection_reason=result.experiment.get("rejection_reason", ""),
        tags=result.experiment.get("tags") or [],
        reproducibility_score=float(result.experiment.get("reproducibility_score") or 0),
        confidence=float(result.experiment.get("confidence") or 0),
    )
    db.add_all([hyp, strat, exp])
    db.commit()
    write_audit(
        "research_cycle_persisted",
        details={
            "experiment_id": str(exp.id),
            "strategy_id": str(strat.id),
            "accepted": result.accepted,
        },
    )
    return {
        "hypothesis_id": str(hyp.id),
        "strategy_id": str(strat.id),
        "experiment_id": str(exp.id),
        "accepted": result.accepted,
    }
