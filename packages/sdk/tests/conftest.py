import pytest

from amini import Amini, AminiConfig


@pytest.fixture
def config():
    return AminiConfig(
        api_key="test-key",
        agent_id="test-agent",
        environment="test",
        base_url="http://localhost:8000",
        enabled=False,
    )


@pytest.fixture
def amini(config):
    client = Amini(config=config)
    yield client
    client.shutdown()
