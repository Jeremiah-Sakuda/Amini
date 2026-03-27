from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EventType(str, Enum):
    SESSION_START = "session.start"
    SESSION_END = "session.end"
    DECISION_START = "decision.start"
    DECISION_INPUT = "decision.input"
    DECISION_REASONING = "decision.reasoning"
    DECISION_ACTION = "decision.action"
    DECISION_OUTPUT = "decision.output"
    DECISION_ERROR = "decision.error"
    DECISION_END = "decision.end"


@dataclass
class Event:
    event_type: EventType
    agent_id: str
    session_id: str
    decision_id: str | None = None
    environment: str = "development"
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sdk_timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "decision_id": self.decision_id,
            "environment": self.environment,
            "payload": self.payload,
            "sdk_timestamp": self.sdk_timestamp,
        }
