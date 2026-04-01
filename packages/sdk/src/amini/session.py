from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field


@dataclass
class SessionInfo:
    session_id: str
    agent_id: str
    environment: str
    user_context: dict | None = None
    metadata: dict | None = None
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    regulations: list[str] = field(default_factory=list)
    framework: str = ""


class SessionManager:
    def __init__(self) -> None:
        self._local = threading.local()
        self._lock = threading.Lock()

    @property
    def current(self) -> SessionInfo | None:
        return getattr(self._local, "session", None)

    def start_session(
        self,
        agent_id: str,
        environment: str,
        session_id: str | None = None,
        user_context: dict | None = None,
        metadata: dict | None = None,
        correlation_id: str | None = None,
        regulations: list[str] | None = None,
        framework: str = "",
    ) -> SessionInfo:
        session = SessionInfo(
            session_id=session_id or str(uuid.uuid4()),
            agent_id=agent_id,
            environment=environment,
            user_context=user_context,
            metadata=metadata,
            correlation_id=correlation_id or str(uuid.uuid4()),
            regulations=regulations or [],
            framework=framework,
        )
        self._local.session = session
        return session

    def end_session(self) -> SessionInfo | None:
        session = self.current
        self._local.session = None
        return session
