from __future__ import annotations

import json
import logging
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.decision import DecisionNode
from ..models.event import RawEvent
from ..models.session import AgentSession, SessionStatus
from .session_service import get_or_create_session

logger = logging.getLogger("amini.chain_builder")


def _event_sort_key(event: RawEvent) -> tuple:
    """Build a sort key that prefers logical sequence over wall-clock time.

    Events emitted by the SDK carry a ``sequence_number`` inside their payload.
    Using this as the primary sort key makes ordering deterministic regardless
    of clock skew between agents running on different machines.  The
    ``sdk_timestamp`` is retained only as a tie-breaker for events that lack a
    sequence number (e.g. older SDK versions).
    """
    payload = event.payload or {}
    seq = payload.get("sequence_number")
    # Use a large sentinel so events without a sequence sort after sequenced ones
    # when mixed, but still sort among themselves by timestamp.
    return (seq if seq is not None else float("inf"), event.sdk_timestamp)


async def build_chain_from_events(
    db: AsyncSession, events: list[RawEvent]
) -> list[DecisionNode]:
    """Reconstruct decision nodes from raw events.

    Groups events by decision_id, orders by logical sequence number (with
    sdk_timestamp as fallback for clock-skew resilience).
    Creates DecisionNode records in the database.
    """
    # Group events by session
    by_session: dict[str, list[RawEvent]] = defaultdict(list)
    for event in events:
        by_session[event.session_id].append(event)

    created_nodes: list[DecisionNode] = []

    for session_ext_id, session_events in by_session.items():
        session_events.sort(key=_event_sort_key)

        # Ensure session exists
        first = session_events[0]
        session = await get_or_create_session(
            db,
            agent_external_id=first.agent_id,
            session_external_id=session_ext_id,
            environment=first.environment,
        )

        # Handle session-level events
        for event in session_events:
            if event.event_type == "session.end":
                payload = event.payload or {}
                raw_status = payload.get("status", "completed")
                try:
                    session.status = SessionStatus(raw_status)
                except ValueError:
                    session.status = SessionStatus.COMPLETED
                session.terminal_reason = payload.get("reason")

        # Group decision events by decision_id
        by_decision: dict[str, list[RawEvent]] = defaultdict(list)
        for event in session_events:
            if event.decision_id and event.event_type.startswith("decision."):
                by_decision[event.decision_id].append(event)

        # Order decisions by the earliest sequence number (or timestamp) of
        # their first event so that the session-level sequence_counter
        # reflects logical ordering rather than wall-clock arrival order.
        ordered_decisions = sorted(
            by_decision.items(),
            key=lambda pair: _event_sort_key(min(pair[1], key=_event_sort_key)),
        )

        # Process each decision group
        sequence_counter = 0
        for decision_ext_id, decision_events in ordered_decisions:
            decision_events.sort(key=_event_sort_key)

            # Check if node already exists (idempotent)
            existing = await db.execute(
                select(DecisionNode).where(
                    DecisionNode.decision_external_id == decision_ext_id,
                    DecisionNode.session_id == session.id,
                )
            )
            if existing.scalar_one_or_none() is not None:
                continue

            sequence_counter += 1
            node = _build_decision_node(
                session_id=session.id,
                decision_ext_id=decision_ext_id,
                events=decision_events,
                sequence=sequence_counter,
            )
            db.add(node)
            created_nodes.append(node)

    await db.flush()

    # Resolve parent_decision_id from external UUID to internal UUID
    for node in created_nodes:
        if node._parent_external_id:
            parent_result = await db.execute(
                select(DecisionNode.id).where(
                    DecisionNode.decision_external_id == node._parent_external_id,
                    DecisionNode.session_id == node.session_id,
                )
            )
            parent_internal_id = parent_result.scalar_one_or_none()
            if parent_internal_id:
                node.parent_decision_id = parent_internal_id
    if created_nodes:
        await db.flush()

    return created_nodes


def _build_decision_node(
    session_id: str,
    decision_ext_id: str,
    events: list[RawEvent],
    sequence: int,
) -> DecisionNode:
    """Build a DecisionNode from a group of related events."""
    node = DecisionNode(
        session_id=session_id,
        decision_external_id=decision_ext_id,
        sequence_number=sequence,
    )
    # Temporary attribute to hold external parent ID for later resolution
    node._parent_external_id = None  # type: ignore[attr-defined]

    for event in events:
        payload = event.payload or {}

        if event.event_type == "decision.start":
            node.decision_type = payload.get("name", "generic")
            parent_id = payload.get("parent_decision_id")
            if parent_id:
                node._parent_external_id = parent_id  # type: ignore[attr-defined]

        elif event.event_type == "decision.input":
            node.input_context = payload

        elif event.event_type == "decision.reasoning":
            node.reasoning_trace = json.dumps(payload)

        elif event.event_type == "decision.action":
            node.action_type = payload.get("action_type")
            node.action_detail = payload

        elif event.event_type == "decision.output":
            node.output = payload

        elif event.event_type == "decision.error":
            node.has_error = True
            node.side_effects = payload

        elif event.event_type == "decision.end":
            node.duration_ms = payload.get("duration_ms")
            if payload.get("has_error"):
                node.has_error = True

    return node
