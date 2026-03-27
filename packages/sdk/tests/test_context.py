from amini.context import DecisionContext
from amini.events import Event, EventType


def test_decision_context_lifecycle():
    events: list[Event] = []

    with DecisionContext(
        name="test-decision",
        agent_id="agent-1",
        session_id="session-1",
        environment="test",
        emit_fn=events.append,
    ) as ctx:
        ctx.log_input({"query": "hello"})
        ctx.log_reasoning({"model": "gpt-4"})
        ctx.log_action("tool_call", {"tool": "search"})
        ctx.log_output({"result": "world"})

    assert len(events) == 6  # start, input, reasoning, action, output, end
    assert events[0].event_type == EventType.DECISION_START
    assert events[1].event_type == EventType.DECISION_INPUT
    assert events[2].event_type == EventType.DECISION_REASONING
    assert events[3].event_type == EventType.DECISION_ACTION
    assert events[4].event_type == EventType.DECISION_OUTPUT
    assert events[5].event_type == EventType.DECISION_END


def test_decision_context_error():
    events: list[Event] = []

    try:
        with DecisionContext(
            name="error-decision",
            agent_id="agent-1",
            session_id="session-1",
            environment="test",
            emit_fn=events.append,
        ) as ctx:
            ctx.log_input({"query": "hello"})
            raise ValueError("something went wrong")
    except ValueError:
        pass

    assert len(events) == 4  # start, input, error, end
    assert events[2].event_type == EventType.DECISION_ERROR
    assert events[3].event_type == EventType.DECISION_END
    assert events[3].payload["has_error"] is True


def test_decision_context_sequence_numbers():
    events: list[Event] = []

    with DecisionContext(
        name="seq-test",
        agent_id="a",
        session_id="s",
        environment="test",
        emit_fn=events.append,
    ) as ctx:
        ctx.log_input({"a": 1})
        ctx.log_output({"b": 2})

    sequences = [e.payload["sequence_number"] for e in events]
    assert sequences == [1, 2, 3, 4]
