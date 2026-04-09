"""Data retention service — cleans up records older than the configured retention period."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..models.audit_report import AuditReport
from ..models.decision import DecisionNode
from ..models.event import RawEvent
from ..models.incident import Incident
from ..models.session import AgentSession
from ..models.violation import PolicyViolation

logger = logging.getLogger("amini.retention")


async def cleanup_expired_data(db: AsyncSession) -> dict[str, int]:
    """Delete records older than retention_days.

    Returns a summary of deleted record counts by table.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.retention_days)
    deleted: dict[str, int] = {}

    # Delete in FK-safe order: children before parents

    # 1. Delete old raw events (no FK dependents)
    result = await db.execute(
        delete(RawEvent).where(RawEvent.created_at < cutoff)
    )
    deleted["events"] = result.rowcount  # type: ignore[assignment]

    # 2. Delete old audit reports (no FK dependents)
    result = await db.execute(
        delete(AuditReport).where(AuditReport.created_at < cutoff)
    )
    deleted["audit_reports"] = result.rowcount  # type: ignore[assignment]

    # 3. Delete incidents before violations (incident.violation_id -> policy_violations)
    result = await db.execute(
        delete(Incident).where(Incident.created_at < cutoff)
    )
    deleted["incidents"] = result.rowcount  # type: ignore[assignment]

    # 4. Delete violations before sessions (violation.session_id -> agent_sessions)
    result = await db.execute(
        delete(PolicyViolation).where(PolicyViolation.created_at < cutoff)
    )
    deleted["violations"] = result.rowcount  # type: ignore[assignment]

    # 5. Delete decision nodes before sessions (decision_node.session_id -> agent_sessions)
    result = await db.execute(
        delete(DecisionNode).where(DecisionNode.created_at < cutoff)
    )
    deleted["decision_nodes"] = result.rowcount  # type: ignore[assignment]

    # 6. Delete old sessions last (parent of violations, decisions, incidents)
    result = await db.execute(
        delete(AgentSession).where(AgentSession.created_at < cutoff)
    )
    deleted["sessions"] = result.rowcount  # type: ignore[assignment]

    await db.commit()
    logger.info(
        "Retention cleanup (cutoff=%s): deleted %s",
        cutoff.isoformat(), deleted,
    )
    return deleted
