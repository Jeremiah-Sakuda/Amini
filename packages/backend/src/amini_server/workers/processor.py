from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.policy import PolicyVersion
from ..models.violation import PolicyViolation
from ..models.agent import Agent
from ..models.session import AgentSession
from ..services.chain_builder import build_chain_from_events
from ..services.event_service import get_unprocessed_events, mark_events_processed
from ..services.policy_engine import evaluate_session
from ..services.violation_service import record_violation

logger = logging.getLogger("amini.processor")

# Module-level lock prevents concurrent processing runs
_processing_lock = asyncio.Lock()


async def process_pending_events(db: AsyncSession) -> int:
    """Process unprocessed events: build chains, evaluate policies, record violations.

    Uses an asyncio lock to prevent concurrent processing runs that could
    cause duplicate chain building or violation recording.
    """
    if _processing_lock.locked():
        logger.debug("Processing already in progress, skipping")
        return 0

    async with _processing_lock:
        events = await get_unprocessed_events(db, limit=200)
        if not events:
            return 0

        # Build decision chains
        nodes = await build_chain_from_events(db, events)

        # Mark events as processed
        event_ids = [e.id for e in events]
        await mark_events_processed(db, event_ids)

        # Get unique session IDs from new nodes
        session_ids = {node.session_id for node in nodes}

        # Load active policy versions
        pv_result = await db.execute(
            select(PolicyVersion).where(PolicyVersion.is_active == True)  # noqa: E712
        )
        policy_versions = list(pv_result.scalars().all())

        # Evaluate policies for each affected session
        violation_count = 0
        for session_id in session_ids:
            session_result = await db.execute(
                select(AgentSession)
                .options(
                    selectinload(AgentSession.decisions),
                    selectinload(AgentSession.agent),
                )
                .where(AgentSession.id == session_id)
            )
            session = session_result.scalar_one_or_none()
            if not session:
                continue

            # Load existing violations to prevent duplicates
            existing_result = await db.execute(
                select(PolicyViolation.policy_version_id).where(
                    PolicyViolation.session_id == session_id
                )
            )
            existing_pv_ids = set(existing_result.scalars().all())

            results = evaluate_session(session, session.decisions, policy_versions)
            for result in results:
                if result.violated and result.policy_version_id not in existing_pv_ids:
                    await record_violation(
                        db,
                        session_id=session_id,
                        policy_version_id=result.policy_version_id,
                        severity=result.severity,
                        violation_type="policy_violation",
                        description=result.message,
                        evidence=result.evidence,
                    )
                    existing_pv_ids.add(result.policy_version_id)
                    violation_count += 1

        await db.commit()
        logger.info(
            "Processed %d events, created %d nodes, recorded %d violations",
            len(events), len(nodes), violation_count,
        )
        return len(events)
