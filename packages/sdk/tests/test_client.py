import logging

import pytest

from amini import Amini, AminiConfig, PolicyViolationError, PolicyRule, PolicyTier, PolicyEnforcement, PolicySeverity


def test_client_init():
    client = Amini(api_key="key", agent_id="agent-1", environment="test")
    assert client._config.api_key == "key"
    assert client._config.agent_id == "agent-1"
    client.shutdown()


def test_client_from_config():
    config = AminiConfig(api_key="k", agent_id="a", enabled=False)
    client = Amini(config=config)
    assert client._config.api_key == "k"
    client.shutdown()


def test_client_with_regulations():
    client = Amini(
        api_key="key",
        agent_id="agent-1",
        regulations=["eu-ai-act", "sox", "ccpa"],
    )
    assert client._config.regulations == ["eu-ai-act", "sox", "ccpa"]
    client.shutdown()


def test_client_with_framework():
    client = Amini(
        api_key="key",
        agent_id="agent-1",
        framework="langchain",
    )
    assert client._config.framework == "langchain"
    client.shutdown()


def test_start_end_session(amini):
    session = amini.start_session(user_context={"user": "test"})
    assert session.session_id
    assert session.agent_id == "test-agent"
    assert session.correlation_id
    assert amini.current_session is not None
    amini.end_session()
    assert amini.current_session is None


def test_session_carries_regulations():
    config = AminiConfig(
        api_key="k",
        agent_id="a",
        enabled=False,
        regulations=["eu-ai-act"],
    )
    client = Amini(config=config)
    session = client.start_session()
    assert session.regulations == ["eu-ai-act"]
    client.shutdown()


def test_session_correlation_id(amini):
    session = amini.start_session()
    assert amini.correlation_id == session.correlation_id
    amini.end_session()
    assert amini.correlation_id is None


def test_session_explicit_correlation_id(amini):
    session = amini.start_session(correlation_id="my-trace-123")
    assert session.correlation_id == "my-trace-123"
    assert amini.correlation_id == "my-trace-123"
    amini.end_session()


def test_trace_decorator_sync(amini):
    @amini.trace
    def my_func(x: int) -> int:
        return x * 2

    amini.start_session()
    result = my_func(5)
    assert result == 10
    amini.end_session()


def test_trace_decorator_with_name(amini):
    @amini.trace(name="custom-name")
    def my_func():
        return "hello"

    amini.start_session()
    result = my_func()
    assert result == "hello"
    amini.end_session()


def test_trace_decorator_with_framework(amini):
    @amini.trace(name="lc-chain", framework="langchain")
    def my_func():
        return "done"

    amini.start_session()
    result = my_func()
    assert result == "done"
    amini.end_session()


def test_trace_auto_creates_session(amini):
    @amini.trace
    def my_func():
        return 42

    assert amini.current_session is None
    result = my_func()
    assert result == 42
    assert amini.current_session is not None
    amini.end_session()


def test_enforce_decorator_no_policy_cached(amini):
    @amini.enforce("nonexistent-policy")
    def my_func():
        return "ok"

    amini.start_session()
    result = my_func()
    assert result == "ok"
    amini.end_session()


def test_enforce_decorator_with_policy_no_conditions(amini):
    """Policy with no conditions always passes."""
    rule = PolicyRule(
        name="test-policy",
        tier=PolicyTier.DETERMINISTIC,
        enforcement=PolicyEnforcement.LOG_ONLY,
        severity=PolicySeverity.LOW,
    )
    amini._policy_cache.register(rule)

    @amini.enforce("test-policy")
    def my_func():
        return "ok"

    amini.start_session()
    result = my_func()
    assert result == "ok"
    amini.end_session()


def test_enforce_block_raises_on_violation(amini):
    """Policy with conditions that match should block execution."""
    rule = PolicyRule(
        name="block-policy",
        tier=PolicyTier.DETERMINISTIC,
        enforcement=PolicyEnforcement.BLOCK,
        severity=PolicySeverity.HIGH,
        conditions={
            "field": "kwargs.action",
            "operator": "equals",
            "value": "delete",
        },
    )
    amini._policy_cache.register(rule)

    @amini.enforce("block-policy")
    def dangerous_action(action: str):
        return f"did {action}"

    amini.start_session()
    with pytest.raises(PolicyViolationError):
        dangerous_action(action="delete")
    amini.end_session()


def test_enforce_block_allows_non_matching(amini):
    """Policy conditions that don't match should allow execution."""
    rule = PolicyRule(
        name="block-policy-2",
        tier=PolicyTier.DETERMINISTIC,
        enforcement=PolicyEnforcement.BLOCK,
        severity=PolicySeverity.HIGH,
        conditions={
            "field": "kwargs.action",
            "operator": "equals",
            "value": "delete",
        },
    )
    amini._policy_cache.register(rule)

    @amini.enforce("block-policy-2")
    def safe_action(action: str):
        return f"did {action}"

    amini.start_session()
    result = safe_action(action="read")
    assert result == "did read"
    amini.end_session()


def test_enforce_warn_logs_on_violation(amini, caplog):
    """Warn-mode policy should log warning but allow execution."""
    rule = PolicyRule(
        name="warn-policy",
        tier=PolicyTier.DETERMINISTIC,
        enforcement=PolicyEnforcement.WARN,
        severity=PolicySeverity.MEDIUM,
        conditions={
            "field": "kwargs.amount",
            "operator": "greater_than",
            "value": 1000,
        },
    )
    amini._policy_cache.register(rule)

    @amini.enforce("warn-policy")
    def transfer(amount: int):
        return f"transferred {amount}"

    amini.start_session()
    with caplog.at_level(logging.WARNING, logger="amini.client"):
        result = transfer(amount=5000)
    assert result == "transferred 5000"
    assert "warn-policy" in caplog.text
    amini.end_session()


def test_enforce_with_and_conditions(amini):
    """Compound AND conditions should all need to match for violation."""
    rule = PolicyRule(
        name="compound-policy",
        tier=PolicyTier.DETERMINISTIC,
        enforcement=PolicyEnforcement.BLOCK,
        severity=PolicySeverity.CRITICAL,
        conditions={
            "and": [
                {"field": "kwargs.action", "operator": "equals", "value": "delete"},
                {"field": "kwargs.scope", "operator": "equals", "value": "all"},
            ]
        },
    )
    amini._policy_cache.register(rule)

    @amini.enforce("compound-policy")
    def action(action: str, scope: str):
        return "ok"

    amini.start_session()
    # Only one condition matches — should pass
    result = action(action="delete", scope="single")
    assert result == "ok"

    # Both conditions match — should block
    with pytest.raises(PolicyViolationError):
        action(action="delete", scope="all")
    amini.end_session()


def test_enforce_with_not_condition(amini):
    """NOT condition should invert the match."""
    rule = PolicyRule(
        name="not-policy",
        tier=PolicyTier.DETERMINISTIC,
        enforcement=PolicyEnforcement.BLOCK,
        severity=PolicySeverity.HIGH,
        conditions={
            "not": {"field": "kwargs.approved", "operator": "equals", "value": True}
        },
    )
    amini._policy_cache.register(rule)

    @amini.enforce("not-policy")
    def action(approved: bool):
        return "ok"

    amini.start_session()
    # approved=True → NOT matches → condition is false → passes
    result = action(approved=True)
    assert result == "ok"

    # approved=False → NOT doesn't match → condition is true → blocks
    with pytest.raises(PolicyViolationError):
        action(approved=False)
    amini.end_session()
