from __future__ import annotations

import logging
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.decision import DecisionNode
from ..models.event import RawEvent
from ..models.session import AgentSession
from .session_service import get_or_create_session

logger = logging.getLogger("amini.chain_builder")


async def build_chain_from_events(
    db: AsyncSession, events: list[RawEvent]
) -> list[DecisionNode]:
    """Reconstruct decision nodes from raw events.

    Groups events by decision_id, orders by sdk_timestamp + sequence.
    Creates DecisionNode records in the database.
    """
    # Group events by session
    by_session: dict[str, list[RawEvent]] = defaultdict(list)
    for event in events:
        by_session[event.session_id].append(event)

    created_nodes: list[DecisionNode] = []

    for session_ext_id, session_events in by_session.items():
        session_events.sort(key=lambda e: e.sdk_timestamp)

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
                status = payload.get("status", "completed")
                session.status = status
                session.terminal_reason = payload.get("reason")

        # Group decision events by decision_id
        by_decision: dict[str, list[RawEvent]] = defaultdict(list)
        for event in session_events:
            if event.decision_id and event.event_type.startswith("decision."):
                by_decision[event.decision_id].append(event)

        # Process each decision group
        sequence_counter = 0
        for decision_ext_id, decision_events in by_decision.items():
            decision_events.sort(key=lambda e: e.sdk_timestamp)

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

    for event in events:
        payload = event.payload or {}

        if event.event_type == "decision.start":
            node.decision_type = payload.get("name", "generic")
            parent_id = payload.get("parent_decision_id")
            if parent_id:
                node.parent_decision_id = parent_id

        elif event.event_type == "decision.input":
            node.input_context = payload

        elif event.event_type == "decision.reasoning":
            node.reasoning_trace = str(payload)

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
