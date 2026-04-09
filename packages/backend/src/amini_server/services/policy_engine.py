from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

import yaml
from amini_policy_core import (
    compare as _compare,
    evaluate_condition as _evaluate_condition,
    resolve_field as _resolve_field,
)

from ..models.decision import DecisionNode
from ..models.policy import PolicyEnforcement, PolicyTier, PolicyVersion
from ..models.session import AgentSession
from ..models.violation import ViolationSeverity

logger = logging.getLogger("amini.policy_engine")

# Type alias for the semantic judge callback.
# A judge receives (policy_version, context_dict) and returns an EvaluationResult.
SemanticJudgeFn = Callable[["PolicyVersion", dict[str, Any]], "EvaluationResult"]

# Module-level registry for the semantic judge.  Call
# ``register_semantic_judge(fn)`` to plug in an LLM-backed judge.
_semantic_judge: SemanticJudgeFn | None = None


def register_semantic_judge(fn: SemanticJudgeFn) -> None:
    """Register an LLM judge function for semantic policy evaluation.

    The function should accept a ``PolicyVersion`` and a context dict, and
    return an ``EvaluationResult``.  This enables the two-tier model
    (deterministic + LLM-judge) described in the PRD.
    """
    global _semantic_judge
    _semantic_judge = fn
    logger.info("Semantic judge registered: %s", fn.__qualname__)


@dataclass
class EvaluationResult:
    violated: bool
    policy_version_id: str
    severity: str
    message: str
    evidence: dict | None = None
    deferred: bool = False


def load_policy(yaml_content: str) -> dict:
    """Parse and validate a policy YAML string."""
    parsed = yaml.safe_load(yaml_content)
    if not isinstance(parsed, dict):
        raise ValueError("Policy YAML must be a mapping")
    required = {"name", "tier", "enforcement", "severity", "message"}
    missing = required - set(parsed.keys())
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    return parsed


def evaluate_session(
    session: AgentSession,
    decisions: list[DecisionNode],
    policy_versions: list[PolicyVersion],
) -> list[EvaluationResult]:
    """Evaluate all active deterministic policies against a session."""
    results = []
    for pv in policy_versions:
        if not pv.is_active:
            continue
        if pv.tier == PolicyTier.SEMANTIC:
            if _semantic_judge is not None:
                session_context = _build_session_context(session, decisions)
                try:
                    result = _semantic_judge(pv, session_context)
                    results.append(result)
                except Exception:
                    logger.exception(
                        "Semantic judge failed for policy %s; deferring",
                        pv.id,
                    )
                    results.append(EvaluationResult(
                        violated=False,
                        policy_version_id=pv.id,
                        severity=pv.severity,
                        message="Semantic judge error — deferred for async advisory review",
                        deferred=True,
                    ))
            else:
                results.append(EvaluationResult(
                    violated=False,
                    policy_version_id=pv.id,
                    severity=pv.severity,
                    message="No semantic judge registered — deferred for async advisory review",
                    deferred=True,
                ))
            continue

        if not _match_scope(pv.scope, session):
            continue

        parsed = pv.parsed_rule or {}
        condition = parsed.get("condition")
        if not condition:
            continue

        # Session-level evaluation
        session_context = _build_session_context(session, decisions)
        if _evaluate_condition(condition, session_context):
            results.append(EvaluationResult(
                violated=True,
                policy_version_id=pv.id,
                severity=pv.severity,
                message=parsed.get("message", pv.message),
                evidence={"context": "session-level evaluation"},
            ))
            continue

        # Decision-level evaluation
        for decision in decisions:
            decision_ctx = _build_decision_context(decision)
            if _evaluate_condition(condition, decision_ctx):
                results.append(EvaluationResult(
                    violated=True,
                    policy_version_id=pv.id,
                    severity=pv.severity,
                    message=parsed.get("message", pv.message),
                    evidence={"decision_id": decision.id},
                ))
                break  # one violation per policy per session

    return results


def evaluate_decision(
    decision: DecisionNode,
    policy_versions: list[PolicyVersion],
) -> list[EvaluationResult]:
    """Evaluate a single decision node against deterministic policies."""
    results = []
    for pv in policy_versions:
        if not pv.is_active or pv.tier == PolicyTier.SEMANTIC:
            continue

        parsed = pv.parsed_rule or {}
        condition = parsed.get("condition")
        if not condition:
            continue

        context = _build_decision_context(decision)
        if _evaluate_condition(condition, context):
            results.append(EvaluationResult(
                violated=True,
                policy_version_id=pv.id,
                severity=pv.severity,
                message=parsed.get("message", pv.message),
                evidence={"decision_id": decision.id},
            ))

    return results


def _match_scope(scope: dict | None, session: AgentSession) -> bool:
    """Check if a policy scope matches the session."""
    if not scope:
        return True

    environments = scope.get("environments")
    if environments and session.environment not in environments:
        return False

    agents = scope.get("agents")
    if agents:
        # Compare against agent_external_id (what the SDK sends), not internal UUID
        agent_ext_id = session.agent.agent_external_id if session.agent else session.agent_id
        if agent_ext_id not in agents:
            return False

    return True


def _build_session_context(
    session: AgentSession, decisions: list[DecisionNode]
) -> dict[str, Any]:
    """Build evaluation context from session data."""
    error_count = sum(1 for d in decisions if d.has_error)
    action_types = [d.action_type for d in decisions if d.action_type]
    unique_actions = set(action_types)

    return {
        "session": {
            "status": session.status.value if hasattr(session.status, "value") else str(session.status),
            "environment": session.environment,
            "decision_count": len(decisions),
            "error_count": error_count,
            "unique_action_ratio": (
                len(unique_actions) / len(action_types) if action_types else 1.0
            ),
            "total_tokens": sum(
                (d.action_detail or {}).get("tokens", 0) for d in decisions
            ),
        },
    }


def _build_decision_context(decision: DecisionNode) -> dict[str, Any]:
    """Build evaluation context from a single decision."""
    return {
        "action_type": decision.action_type or "",
        "has_error": decision.has_error,
        "duration_ms": decision.duration_ms or 0,
        "input_context": str(decision.input_context or ""),
        "output": str(decision.output or ""),
        "decision_type": decision.decision_type,
    }


# _evaluate_condition, _resolve_field, and _compare are imported from
# amini_policy_core at the top of this module.  This eliminates the previous
# copy-paste duplication and guarantees the SDK and backend always evaluate
# conditions identically.
