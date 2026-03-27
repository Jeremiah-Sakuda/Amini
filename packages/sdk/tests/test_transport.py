from unittest.mock import MagicMock, patch

from amini.config import AminiConfig
from amini.events import Event, EventType
from amini.transport import HttpTransport


def _make_event() -> Event:
    return Event(
        event_type=EventType.DECISION_START,
        agent_id="agent-1",
        session_id="session-1",
    )


def test_send_batch_empty():
    config = AminiConfig(base_url="http://localhost:8000")
    transport = HttpTransport(config)
    assert transport.send_batch([]) is True
    transport.close()


@patch("amini.transport.httpx.Client")
def test_send_batch_posts(mock_client_cls):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_client.post.return_value = mock_response
    mock_client_cls.return_value = mock_client

    config = AminiConfig(base_url="http://localhost:8000", api_key="test-key")
    transport = HttpTransport(config)

    events = [_make_event(), _make_event()]
    result = transport.send_batch(events)

    assert result is True
    mock_client.post.assert_called_once()
    call_args = mock_client.post.call_args
    assert call_args[0][0] == "/api/v1/events/batch"
    transport.close()
