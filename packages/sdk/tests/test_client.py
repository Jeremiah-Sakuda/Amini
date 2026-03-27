from amini import Amini, AminiConfig


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


def test_start_end_session(amini):
    session = amini.start_session(user_context={"user": "test"})
    assert session.session_id
    assert session.agent_id == "test-agent"
    assert amini.current_session is not None
    amini.end_session()
    assert amini.current_session is None


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


def test_trace_auto_creates_session(amini):
    @amini.trace
    def my_func():
        return 42

    assert amini.current_session is None
    result = my_func()
    assert result == 42
    assert amini.current_session is not None
    amini.end_session()
