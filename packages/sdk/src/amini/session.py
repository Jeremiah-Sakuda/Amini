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
    ) -> SessionInfo:
        session = SessionInfo(
            session_id=session_id or str(uuid.uuid4()),
            agent_id=agent_id,
            environment=environment,
            user_context=user_context,
            metadata=metadata,
        )
        self._local.session = session
        return session

    def end_session(self) -> SessionInfo | None:
        session = self.current
        self._local.session = None
        return session
