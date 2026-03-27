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
            payload={"name": "my-decision"}, sdk_timestamp=now,
        ),
        RawEvent(
            event_type="decision.input", agent_id="agent-1",
            session_id=sid, decision_id=did, environment="test",
            payload={"query": "test"}, sdk_timestamp=now + 0.1,
        ),
        RawEvent(
            event_type="decision.end", agent_id="agent-1",
            session_id=sid, decision_id=did, environment="test",
            payload={"duration_ms": 50, "has_error": False}, sdk_timestamp=now + 0.2,
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
            payload={"name": "idempotent-test"}, sdk_timestamp=now,
        ),
        RawEvent(
            event_type="decision.end", agent_id="agent-1",
            session_id=sid, decision_id=did, environment="test",
            payload={"duration_ms": 10, "has_error": False}, sdk_timestamp=now + 0.1,
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
