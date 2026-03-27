import time
from unittest.mock import MagicMock

from amini.config import AminiConfig
from amini.emitter import EventEmitter
from amini.events import Event, EventType


def _make_event(**kwargs) -> Event:
    defaults = {
        "event_type": EventType.DECISION_START,
        "agent_id": "agent-1",
        "session_id": "session-1",
    }
    defaults.update(kwargs)
    return Event(**defaults)


def test_emitter_queues_events():
    config = AminiConfig(enabled=True, flush_interval_seconds=100)
    transport = MagicMock()
    emitter = EventEmitter(config, transport=transport)

    emitter.emit(_make_event())
    emitter.emit(_make_event())

    emitter.flush()
    transport.send_batch.assert_called_once()
    batch = transport.send_batch.call_args[0][0]
    assert len(batch) == 2


def test_emitter_disabled():
    config = AminiConfig(enabled=False)
    transport = MagicMock()
    emitter = EventEmitter(config, transport=transport)

    emitter.emit(_make_event())
    emitter.flush()
    transport.send_batch.assert_not_called()


def test_emitter_shutdown():
    config = AminiConfig(enabled=True, flush_interval_seconds=100)
    transport = MagicMock()
    transport.send_batch.return_value = True
    emitter = EventEmitter(config, transport=transport)
    emitter.start()

    emitter.emit(_make_event())
    emitter.shutdown(timeout=2.0)

    transport.close.assert_called_once()
