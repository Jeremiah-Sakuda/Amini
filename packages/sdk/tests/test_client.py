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


def test_enforce_decorator_with_policy(amini):
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
