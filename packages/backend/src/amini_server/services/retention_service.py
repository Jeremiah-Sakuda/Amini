"""Data retention service — cleans up records older than the configured retention period."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..models.event import RawEvent
from ..models.session import AgentSession
from ..models.violation import PolicyViolation as Violation

logger = logging.getLogger("amini.retention")


async def cleanup_expired_data(db: AsyncSession) -> dict[str, int]:
    """Delete records older than retention_days.

    Returns a summary of deleted record counts by table.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.retention_days)
    deleted: dict[str, int] = {}

    # Delete old raw events
    result = await db.execute(
        delete(RawEvent).where(RawEvent.server_timestamp < cutoff)
    )
    deleted["events"] = result.rowcount  # type: ignore[assignment]

    # Delete old violations
    result = await db.execute(
        delete(Violation).where(Violation.created_at < cutoff)
    )
    deleted["violations"] = result.rowcount  # type: ignore[assignment]

    # Delete old sessions
    result = await db.execute(
        delete(AgentSession).where(AgentSession.started_at < cutoff)
    )
    deleted["sessions"] = result.rowcount  # type: ignore[assignment]

    await db.commit()
    logger.info(
        "Retention cleanup (cutoff=%s): deleted %s",
        cutoff.isoformat(), deleted,
    )
    return deleted
