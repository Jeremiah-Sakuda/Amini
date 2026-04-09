from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from amini_policy_core import (
    compare as _compare,
    evaluate_condition,
    resolve_field as _resolve_field,
)

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
# Condition evaluator — delegates to amini_policy_core (single source of truth)
# ---------------------------------------------------------------------------
# evaluate_condition, _resolve_field, and _compare are imported from
# amini_policy_core at the top of this module.  Re-exported here so existing
# SDK consumers that import ``from amini.policy import evaluate_condition``
# continue to work without changes.

__all__ = [
    "PolicyTier",
    "PolicyEnforcement",
    "PolicySeverity",
    "PolicyResult",
    "PolicyViolationError",
    "PolicyRule",
    "PolicyCache",
    "evaluate_condition",
    "_resolve_field",
    "_compare",
]
