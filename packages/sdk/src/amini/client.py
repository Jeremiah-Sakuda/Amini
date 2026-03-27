from __future__ import annotations

import asyncio
import functools
import inspect
from typing import Any, Callable, TypeVar

from .config import AminiConfig
from .context import DecisionContext
from .emitter import EventEmitter
from .events import Event, EventType
from .session import SessionInfo, SessionManager

F = TypeVar("F", bound=Callable[..., Any])


class Amini:
    def __init__(
        self,
        api_key: str | None = None,
        agent_id: str | None = None,
        environment: str | None = None,
        base_url: str | None = None,
        config: AminiConfig | None = None,
    ) -> None:
        if config:
            self._config = config
        else:
            self._config = AminiConfig.from_env()
            if api_key:
                self._config.api_key = api_key
            if agent_id:
                self._config.agent_id = agent_id
            if environment:
                self._config.environment = environment
            if base_url:
                self._config.base_url = base_url

        self._emitter = EventEmitter(self._config)
        self._sessions = SessionManager()
        self._emitter.start()

    @property
    def current_session(self) -> SessionInfo | None:
        return self._sessions.current

    def start_session(
        self,
        session_id: str | None = None,
        user_context: dict | None = None,
        metadata: dict | None = None,
    ) -> SessionInfo:
        session = self._sessions.start_session(
            agent_id=self._config.agent_id,
            environment=self._config.environment,
            session_id=session_id,
            user_context=user_context,
            metadata=metadata,
        )
        self._emitter.emit(Event(
            event_type=EventType.SESSION_START,
            agent_id=self._config.agent_id,
            session_id=session.session_id,
            environment=self._config.environment,
            payload={
                "user_context": user_context,
                "metadata": metadata,
            },
        ))
        return session

    def end_session(self, status: str = "completed", reason: str | None = None) -> None:
        session = self._sessions.end_session()
        if session:
            self._emitter.emit(Event(
                event_type=EventType.SESSION_END,
                agent_id=self._config.agent_id,
                session_id=session.session_id,
                environment=self._config.environment,
                payload={"status": status, "reason": reason},
            ))

    def decision(
        self, name: str, parent_decision_id: str | None = None
    ) -> DecisionContext:
        session = self._sessions.current
        if not session:
            session = self.start_session()
        return DecisionContext(
            name=name,
            agent_id=self._config.agent_id,
            session_id=session.session_id,
            environment=self._config.environment,
            emit_fn=self._emitter.emit,
            parent_decision_id=parent_decision_id,
        )

    def trace(self, func: F | None = None, *, name: str | None = None) -> F | Callable[[F], F]:
        def decorator(fn: F) -> F:
            decision_name = name or fn.__qualname__

            if inspect.iscoroutinefunction(fn):
                @functools.wraps(fn)
                async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                    with self.decision(decision_name) as ctx:
                        ctx.log_input({"args": _safe_repr(args), "kwargs": _safe_repr(kwargs)})
                        result = await fn(*args, **kwargs)
                        ctx.log_output({"result": _safe_repr(result)})
                        return result
                return async_wrapper  # type: ignore
            else:
                @functools.wraps(fn)
                def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                    with self.decision(decision_name) as ctx:
                        ctx.log_input({"args": _safe_repr(args), "kwargs": _safe_repr(kwargs)})
                        result = fn(*args, **kwargs)
                        ctx.log_output({"result": _safe_repr(result)})
                        return result
                return sync_wrapper  # type: ignore

        if func is not None:
            return decorator(func)
        return decorator

    def flush(self) -> None:
        self._emitter.flush()

    def shutdown(self) -> None:
        self._emitter.shutdown()


def _safe_repr(obj: Any) -> Any:
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {k: _safe_repr(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_safe_repr(item) for item in obj]
    try:
        return str(obj)
    except Exception:
        return "<unrepresentable>"
