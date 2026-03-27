from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

import yaml

from ..models.decision import DecisionNode
from ..models.policy import PolicyEnforcement, PolicyTier, PolicyVersion
from ..models.session import AgentSession
from ..models.violation import ViolationSeverity

logger = logging.getLogger("amini.policy_engine")


@dataclass
class EvaluationResult:
    violated: bool
    policy_version_id: str
    severity: str
    message: str
    evidence: dict | None = None


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
            results.append(EvaluationResult(
                violated=False,
                policy_version_id=pv.id,
                severity=pv.severity,
                message="Semantic evaluation not implemented (stub)",
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
    if agents and session.agent_id not in agents:
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


def _evaluate_condition(condition: dict, context: dict[str, Any]) -> bool:
    """Safe recursive-descent evaluation of condition DSL. No eval()."""
    if "and" in condition:
        return all(_evaluate_condition(c, context) for c in condition["and"])
    if "or" in condition:
        return any(_evaluate_condition(c, context) for c in condition["or"])
    if "not" in condition:
        return not _evaluate_condition(condition["not"], context)

    field = condition.get("field", "")
    operator = condition.get("operator", "")
    expected = condition.get("value")

    actual = _resolve_field(field, context)

    return _compare(actual, operator, expected)


def _resolve_field(field: str, context: dict[str, Any]) -> Any:
    """Resolve a dotted field path against context dict."""
    parts = field.split(".")
    current: Any = context
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def _compare(actual: Any, operator: str, expected: Any) -> bool:
    """Safe comparison without eval()."""
    if actual is None:
        return False

    try:
        if operator == "equals":
            return actual == expected
        elif operator == "not_equals":
            return actual != expected
        elif operator == "greater_than":
            return float(actual) > float(expected)
        elif operator == "less_than":
            return float(actual) < float(expected)
        elif operator == "greater_than_or_equal":
            return float(actual) >= float(expected)
        elif operator == "less_than_or_equal":
            return float(actual) <= float(expected)
        elif operator == "contains":
            return str(expected) in str(actual)
        elif operator == "not_contains":
            return str(expected) not in str(actual)
        elif operator == "matches_regex":
            return bool(re.search(str(expected), str(actual)))
        elif operator == "in_list":
            return actual in (expected if isinstance(expected, list) else [expected])
        elif operator == "not_in_list":
            return actual not in (expected if isinstance(expected, list) else [expected])
    except (ValueError, TypeError):
        return False

    return False
