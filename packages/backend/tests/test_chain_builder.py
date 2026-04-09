import json
import time
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from amini_server.models.event import RawEvent
from amini_server.services.chain_builder import build_chain_from_events


@pytest.mark.asyncio
async def test_build_chain_creates_decision_node(db: AsyncSession):
    sid = str(uuid.uuid4())
    did = str(uuid.uuid4())
    now = time.time()

    events = [
        RawEvent(
            event_type="decision.start", agent_id="agent-1",
            session_id=sid, decision_id=did, environment="test",
            payload={"name": "my-decision", "sequence_number": 1}, sdk_timestamp=now,
        ),
        RawEvent(
            event_type="decision.input", agent_id="agent-1",
            session_id=sid, decision_id=did, environment="test",
            payload={"query": "test", "sequence_number": 2}, sdk_timestamp=now + 0.1,
        ),
        RawEvent(
            event_type="decision.end", agent_id="agent-1",
            session_id=sid, decision_id=did, environment="test",
            payload={"duration_ms": 50, "has_error": False, "sequence_number": 3},
            sdk_timestamp=now + 0.2,
        ),
    ]
    for e in events:
        db.add(e)
    await db.flush()

    nodes = await build_chain_from_events(db, events)
    assert len(nodes) == 1
    assert nodes[0].decision_type == "my-decision"
    assert nodes[0].duration_ms == 50
    assert nodes[0].has_error is False


@pytest.mark.asyncio
async def test_build_chain_idempotent(db: AsyncSession):
    sid = str(uuid.uuid4())
    did = str(uuid.uuid4())
    now = time.time()

    events = [
        RawEvent(
            event_type="decision.start", agent_id="agent-1",
            session_id=sid, decision_id=did, environment="test",
            payload={"name": "idempotent-test", "sequence_number": 1},
            sdk_timestamp=now,
        ),
        RawEvent(
            event_type="decision.end", agent_id="agent-1",
            session_id=sid, decision_id=did, environment="test",
            payload={"duration_ms": 10, "has_error": False, "sequence_number": 2},
            sdk_timestamp=now + 0.1,
        ),
    ]
    for e in events:
        db.add(e)
    await db.flush()

    # First build
    nodes1 = await build_chain_from_events(db, events)
    assert len(nodes1) == 1

    # Second build (same events) should not create duplicates
    nodes2 = await build_chain_from_events(db, events)
    assert len(nodes2) == 0


@pytest.mark.asyncio
async def test_build_chain_uses_sequence_over_timestamp(db: AsyncSession):
    """Events with clock skew are ordered correctly using sequence_number."""
    sid = str(uuid.uuid4())
    did = str(uuid.uuid4())
    now = time.time()

    # Intentionally reverse the timestamps vs sequence numbers to simulate
    # clock skew — the chain builder should use sequence_number, not timestamp.
    events = [
        RawEvent(
            event_type="decision.end", agent_id="agent-1",
            session_id=sid, decision_id=did, environment="test",
            payload={"duration_ms": 100, "has_error": False, "sequence_number": 3},
            sdk_timestamp=now - 1,  # earliest timestamp, but highest sequence
        ),
        RawEvent(
            event_type="decision.start", agent_id="agent-1",
            session_id=sid, decision_id=did, environment="test",
            payload={"name": "clock-skew-test", "sequence_number": 1},
            sdk_timestamp=now + 1,  # latest timestamp, but lowest sequence
        ),
        RawEvent(
            event_type="decision.input", agent_id="agent-1",
            session_id=sid, decision_id=did, environment="test",
            payload={"query": "test", "sequence_number": 2},
            sdk_timestamp=now,
        ),
    ]
    for e in events:
        db.add(e)
    await db.flush()

    nodes = await build_chain_from_events(db, events)
    assert len(nodes) == 1
    # The decision.start event (seq 1) should be processed first,
    # setting decision_type correctly
    assert nodes[0].decision_type == "clock-skew-test"
    # The decision.end (seq 3) should be processed last, setting duration
    assert nodes[0].duration_ms == 100


@pytest.mark.asyncio
async def test_reasoning_trace_stored_as_json(db: AsyncSession):
    """reasoning_trace should be valid JSON, not Python repr."""
    sid = str(uuid.uuid4())
    did = str(uuid.uuid4())
    now = time.time()

    reasoning_payload = {"thought": "The user wants X", "confidence": 0.95}

    events = [
        RawEvent(
            event_type="decision.start", agent_id="agent-1",
            session_id=sid, decision_id=did, environment="test",
            payload={"name": "reasoning-test", "sequence_number": 1},
            sdk_timestamp=now,
        ),
        RawEvent(
            event_type="decision.reasoning", agent_id="agent-1",
            session_id=sid, decision_id=did, environment="test",
            payload=reasoning_payload, sdk_timestamp=now + 0.1,
        ),
        RawEvent(
            event_type="decision.end", agent_id="agent-1",
            session_id=sid, decision_id=did, environment="test",
            payload={"duration_ms": 50, "has_error": False, "sequence_number": 3},
            sdk_timestamp=now + 0.2,
        ),
    ]
    for e in events:
        db.add(e)
    await db.flush()

    nodes = await build_chain_from_events(db, events)
    assert len(nodes) == 1

    # Should be valid JSON, not Python repr
    parsed = json.loads(nodes[0].reasoning_trace)
    assert parsed["thought"] == "The user wants X"
    assert parsed["confidence"] == 0.95
