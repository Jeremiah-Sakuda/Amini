from __future__ import annotations

import functools
import inspect
import logging
from typing import Any, Callable, TypeVar

from .config import AminiConfig
from .context import DecisionContext
from .emitter import EventEmitter
from .events import Event, EventType
from .policy import PolicyCache, PolicyResult, PolicySeverity, PolicyViolationError
from .session import SessionInfo, SessionManager

F = TypeVar("F", bound=Callable[..., Any])

logger = logging.getLogger("amini.client")


class Amini:
    def __init__(
        self,
        api_key: str | None = None,
        agent_id: str | None = None,
        environment: str | None = None,
        base_url: str | None = None,
        regulations: list[str] | None = None,
        framework: str | None = None,
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
        if regulations is not None:
            self._config.regulations = regulations
        if framework is not None:
            self._config.framework = framework

        self._emitter = EventEmitter(self._config)
        self._sessions = SessionManager()
        self._policy_cache = PolicyCache()
        self._emitter.start()

    @property
    def current_session(self) -> SessionInfo | None:
        return self._sessions.current

    @property
    def correlation_id(self) -> str | None:
        session = self._sessions.current
        return session.correlation_id if session else None

    def start_session(
        self,
        session_id: str | None = None,
        user_context: dict | None = None,
        metadata: dict | None = None,
        correlation_id: str | None = None,
    ) -> SessionInfo:
        session = self._sessions.start_session(
            agent_id=self._config.agent_id,
            environment=self._config.environment,
            session_id=session_id,
            user_context=user_context,
            metadata=metadata,
            correlation_id=correlation_id,
            regulations=self._config.regulations,
            framework=self._config.framework,
        )
        self._emitter.emit(Event(
            event_type=EventType.SESSION_START,
            agent_id=self._config.agent_id,
            session_id=session.session_id,
            environment=self._config.environment,
            correlation_id=session.correlation_id,
            framework=self._config.framework or None,
            regulations=self._config.regulations,
            payload={
                "user_context": user_context,
                "metadata": metadata,
                "regulations": self._config.regulations,
                "framework": self._config.framework,
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
                correlation_id=session.correlation_id,
                framework=self._config.framework or None,
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
            correlation_id=session.correlation_id,
            framework=self._config.framework or None,
            regulations=self._config.regulations,
        )

    def trace(
        self,
        func: F | None = None,
        *,
        name: str | None = None,
        framework: str | None = None,
    ) -> F | Callable[[F], F]:
        def decorator(fn: F) -> F:
            decision_name = name or fn.__qualname__
            fw = framework or self._config.framework or None

            if inspect.iscoroutinefunction(fn):
                @functools.wraps(fn)
                async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                    session = self._sessions.current
                    if not session:
                        session = self.start_session()
                    ctx = DecisionContext(
                        name=decision_name,
                        agent_id=self._config.agent_id,
                        session_id=session.session_id,
                        environment=self._config.environment,
                        emit_fn=self._emitter.emit,
                        correlation_id=session.correlation_id,
                        framework=fw,
                        regulations=self._config.regulations,
                    )
                    with ctx:
                        ctx.log_input({"args": _safe_repr(args), "kwargs": _safe_repr(kwargs)})
                        result = await fn(*args, **kwargs)
                        ctx.log_output({"result": _safe_repr(result)})
                        return result
                return async_wrapper  # type: ignore
            else:
                @functools.wraps(fn)
                def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                    session = self._sessions.current
                    if not session:
                        session = self.start_session()
                    ctx = DecisionContext(
                        name=decision_name,
                        agent_id=self._config.agent_id,
                        session_id=session.session_id,
                        environment=self._config.environment,
                        emit_fn=self._emitter.emit,
                        correlation_id=session.correlation_id,
                        framework=fw,
                        regulations=self._config.regulations,
                    )
                    with ctx:
                        ctx.log_input({"args": _safe_repr(args), "kwargs": _safe_repr(kwargs)})
                        result = fn(*args, **kwargs)
                        ctx.log_output({"result": _safe_repr(result)})
                        return result
                return sync_wrapper  # type: ignore

        if func is not None:
            return decorator(func)
        return decorator

    def enforce(
        self,
        policy_name: str,
    ) -> Callable[[F], F]:
        """Decorator for inline deterministic policy enforcement.

        When a policy is registered in the cache and its enforcement mode is
        ``block``, the decorated function will raise ``PolicyViolationError``
        if the policy check fails.  In ``warn`` mode a warning is logged.
        In ``log_only`` mode the violation is emitted as an event only.
        """
        def decorator(fn: F) -> F:
            if inspect.iscoroutinefunction(fn):
                @functools.wraps(fn)
                async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                    self._check_policy(policy_name, fn, args, kwargs)
                    return await fn(*args, **kwargs)
                return async_wrapper  # type: ignore
            else:
                @functools.wraps(fn)
                def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                    self._check_policy(policy_name, fn, args, kwargs)
                    return fn(*args, **kwargs)
                return sync_wrapper  # type: ignore
        return decorator

    def _check_policy(
        self,
        policy_name: str,
        fn: Callable,
        args: tuple,
        kwargs: dict,
    ) -> None:
        policy = self._policy_cache.get(policy_name)
        if policy is None:
            logger.debug("Policy '%s' not found in cache, skipping enforcement", policy_name)
            return

        result = PolicyResult(
            policy_name=policy_name,
            passed=True,
            enforcement=policy.enforcement,
            severity=policy.severity,
        )

        session = self._sessions.current
        if session:
            self._emitter.emit(Event(
                event_type=EventType.POLICY_VIOLATION,
                agent_id=self._config.agent_id,
                session_id=session.session_id,
                environment=self._config.environment,
                correlation_id=session.correlation_id,
                payload={
                    "policy_name": policy_name,
                    "passed": result.passed,
                    "enforcement": result.enforcement.value,
                    "severity": result.severity.value,
                    "function": fn.__qualname__,
                },
            ))

        if not result.passed:
            from .policy import PolicyEnforcement
            if policy.enforcement == PolicyEnforcement.BLOCK:
                raise PolicyViolationError(result)
            elif policy.enforcement == PolicyEnforcement.WARN:
                logger.warning(
                    "Policy '%s' violation (warn): %s", policy_name, result.message
                )

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
