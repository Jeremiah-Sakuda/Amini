import time
import uuid


def make_event(
    event_type: str = "decision.start",
    agent_id: str = "test-agent",
    session_id: str | None = None,
    decision_id: str | None = None,
    payload: dict | None = None,
) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "agent_id": agent_id,
        "session_id": session_id or str(uuid.uuid4()),
        "decision_id": decision_id or str(uuid.uuid4()),
        "environment": "test",
        "payload": payload or {},
        "sdk_timestamp": time.time(),
    }


def make_event_batch(
    session_id: str | None = None,
    decision_id: str | None = None,
    agent_id: str = "test-agent",
) -> list[dict]:
    sid = session_id or str(uuid.uuid4())
    did = decision_id or str(uuid.uuid4())
    return [
        make_event("decision.start", agent_id, sid, did, {"name": "test-decision"}),
        make_event("decision.input", agent_id, sid, did, {"query": "hello"}),
        make_event("decision.output", agent_id, sid, did, {"result": "world"}),
        make_event("decision.end", agent_id, sid, did, {"duration_ms": 100, "has_error": False}),
    ]
