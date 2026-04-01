from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("amini.policy")


class PolicyTier(str, Enum):
    DETERMINISTIC = "deterministic"
    SEMANTIC = "semantic"


class PolicyEnforcement(str, Enum):
    BLOCK = "block"
    WARN = "warn"
    LOG_ONLY = "log_only"
    ALERT_ONLY = "alert_only"


class PolicySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PolicyResult:
    policy_name: str
    passed: bool
    enforcement: PolicyEnforcement
    severity: PolicySeverity
    message: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)


class PolicyViolationError(Exception):
    """Raised when an inline policy blocks execution."""

    def __init__(self, result: PolicyResult) -> None:
        self.result = result
        super().__init__(
            f"Policy '{result.policy_name}' blocked execution: {result.message}"
        )


@dataclass
class PolicyRule:
    """A client-side policy rule fetched from the server."""

    name: str
    tier: PolicyTier
    enforcement: PolicyEnforcement
    severity: PolicySeverity
    regulation: str = ""
    article: str = ""
    conditions: dict[str, Any] = field(default_factory=dict)


class PolicyCache:
    """Local cache of policies fetched from the Amini backend."""

    def __init__(self) -> None:
        self._policies: dict[str, PolicyRule] = {}

    def register(self, policy: PolicyRule) -> None:
        self._policies[policy.name] = policy

    def get(self, name: str) -> PolicyRule | None:
        return self._policies.get(name)

    def all(self) -> list[PolicyRule]:
        return list(self._policies.values())

    def clear(self) -> None:
        self._policies.clear()


# ---------------------------------------------------------------------------
# Safe recursive-descent condition evaluator (mirrors backend policy_engine)
# ---------------------------------------------------------------------------

def evaluate_condition(condition: dict, context: dict[str, Any]) -> bool:
    """Evaluate a condition dict against a context using safe recursive descent."""
    if not condition:
        return True
    if "and" in condition:
        return all(evaluate_condition(c, context) for c in condition["and"])
    if "or" in condition:
        return any(evaluate_condition(c, context) for c in condition["or"])
    if "not" in condition:
        return not evaluate_condition(condition["not"], context)

    field = condition.get("field", "")
    operator = condition.get("operator", "")
    expected = condition.get("value")

    actual = _resolve_field(field, context)
    return _compare(actual, operator, expected)


def _resolve_field(field: str, context: dict[str, Any]) -> Any:
    """Resolve a dotted field path against a context dict."""
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
