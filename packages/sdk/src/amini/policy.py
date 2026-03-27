from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


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
class PolicyStub:
    """Client-side policy type stub for future inline enforcement."""

    name: str
    tier: PolicyTier
    enforcement: PolicyEnforcement
    severity: PolicySeverity
