from __future__ import annotations

import time
import uuid
from typing import Any

from .events import Event, EventType


class DecisionContext:
    def __init__(
        self,
        name: str,
        agent_id: str,
        session_id: str,
        environment: str,
        emit_fn: Any,
        parent_decision_id: str | None = None,
        correlation_id: str | None = None,
        framework: str | None = None,
        regulations: list[str] | None = None,
    ) -> None:
        self.name = name
        self.decision_id = str(uuid.uuid4())
        self._agent_id = agent_id
        self._session_id = session_id
        self._environment = environment
        self._emit = emit_fn
        self._parent_decision_id = parent_decision_id
        self._correlation_id = correlation_id
        self._framework = framework
        self._regulations = regulations or []
        self._start_time: float = 0
        self._sequence: int = 0

    def __enter__(self) -> DecisionContext:
        self._start_time = time.time()
        self._emit_event(EventType.DECISION_START, {
            "name": self.name,
            "parent_decision_id": self._parent_decision_id,
        })
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        duration_ms = int((time.time() - self._start_time) * 1000)
        if exc_type is not None:
            self.log_error({
                "error_type": exc_type.__name__,
                "error_message": str(exc_val),
            })
        self._emit_event(EventType.DECISION_END, {
            "duration_ms": duration_ms,
            "has_error": exc_type is not None,
        })

    def log_input(self, data: dict[str, Any]) -> None:
        self._emit_event(EventType.DECISION_INPUT, data)

    def log_reasoning(self, data: dict[str, Any]) -> None:
        self._emit_event(EventType.DECISION_REASONING, data)

    def log_action(self, action_type: str, data: dict[str, Any] | None = None) -> None:
        self._emit_event(EventType.DECISION_ACTION, {
            "action_type": action_type,
            **(data or {}),
        })

    def log_output(self, data: dict[str, Any]) -> None:
        self._emit_event(EventType.DECISION_OUTPUT, data)

    def log_error(self, data: dict[str, Any]) -> None:
        self._emit_event(EventType.DECISION_ERROR, data)

    def _emit_event(self, event_type: EventType, payload: dict[str, Any]) -> None:
        self._sequence += 1
        payload["sequence_number"] = self._sequence
        event = Event(
            event_type=event_type,
            agent_id=self._agent_id,
            session_id=self._session_id,
            decision_id=self.decision_id,
            environment=self._environment,
            payload=payload,
            correlation_id=self._correlation_id,
            framework=self._framework,
            regulations=self._regulations,
        )
        self._emit(event)
