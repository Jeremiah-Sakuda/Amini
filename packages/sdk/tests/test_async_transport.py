"""Tests for the AsyncHttpTransport."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from amini.config import AminiConfig
from amini.events import Event, EventType
from amini.transport import AsyncHttpTransport


def _make_event() -> Event:
    return Event(
        event_type=EventType.DECISION_START,
        agent_id="agent-1",
        session_id="session-1",
    )


@pytest.mark.asyncio
async def test_async_send_batch_empty():
    config = AminiConfig(base_url="http://localhost:8000")
    transport = AsyncHttpTransport(config)
    assert await transport.send_batch([]) is True
    await transport.close()


@pytest.mark.asyncio
async def test_async_send_batch_posts():
    config = AminiConfig(base_url="http://localhost:8000", api_key="test-key")
    transport = AsyncHttpTransport(config)

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    transport._client.post = AsyncMock(return_value=mock_response)

    events = [_make_event(), _make_event()]
    result = await transport.send_batch(events)

    assert result is True
    transport._client.post.assert_called_once()
    call_args = transport._client.post.call_args
    assert call_args[0][0] == "/api/v1/events/batch"
    await transport.close()


@pytest.mark.asyncio
async def test_async_send_batch_retries_on_failure():
    config = AminiConfig(base_url="http://localhost:8000", api_key="test-key")
    transport = AsyncHttpTransport(config)

    mock_response_ok = MagicMock()
    mock_response_ok.raise_for_status = MagicMock()

    transport._client.post = AsyncMock(
        side_effect=[httpx.HTTPError("connection reset"), mock_response_ok]
    )

    with patch("amini.transport.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = await transport.send_batch([_make_event()])

    assert result is True
    assert transport._client.post.call_count == 2
    mock_sleep.assert_called_once()
    await transport.close()


@pytest.mark.asyncio
async def test_async_send_batch_gives_up_after_max_retries():
    config = AminiConfig(base_url="http://localhost:8000", api_key="test-key")
    transport = AsyncHttpTransport(config)

    transport._client.post = AsyncMock(side_effect=httpx.HTTPError("server down"))

    with patch("amini.transport.asyncio.sleep", new_callable=AsyncMock):
        result = await transport.send_batch([_make_event()])

    assert result is False
    assert transport._client.post.call_count == 4  # initial + 3 retries
    await transport.close()
