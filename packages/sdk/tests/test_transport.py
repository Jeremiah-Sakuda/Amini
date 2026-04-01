from unittest.mock import MagicMock, patch

import httpx

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


@patch("amini.transport.time.sleep")
@patch("amini.transport.httpx.Client")
def test_send_batch_retries_on_failure_then_succeeds(mock_client_cls, mock_sleep):
    """Transport retries on transient failure and succeeds on second attempt."""
    mock_client = MagicMock()
    mock_response_ok = MagicMock()
    mock_response_ok.raise_for_status = MagicMock()

    # First call fails, second succeeds
    mock_client.post.side_effect = [
        httpx.HTTPError("connection reset"),
        mock_response_ok,
    ]
    mock_client_cls.return_value = mock_client

    config = AminiConfig(base_url="http://localhost:8000", api_key="test-key")
    transport = HttpTransport(config)
    result = transport.send_batch([_make_event()])

    assert result is True
    assert mock_client.post.call_count == 2
    mock_sleep.assert_called_once()  # slept between retries
    transport.close()


@patch("amini.transport.time.sleep")
@patch("amini.transport.httpx.Client")
def test_send_batch_gives_up_after_max_retries(mock_client_cls, mock_sleep):
    """Transport gives up and returns False after exhausting retries."""
    mock_client = MagicMock()
    mock_client.post.side_effect = httpx.HTTPError("server down")
    mock_client_cls.return_value = mock_client

    config = AminiConfig(base_url="http://localhost:8000", api_key="test-key")
    transport = HttpTransport(config)
    result = transport.send_batch([_make_event()])

    assert result is False
    assert mock_client.post.call_count == 4  # initial + 3 retries
    assert mock_sleep.call_count == 3  # slept between each retry
    transport.close()
