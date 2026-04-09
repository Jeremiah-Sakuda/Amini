from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.event import RawEvent
from ..schemas.events import EventCreate


async def store_event(db: AsyncSession, event: EventCreate) -> RawEvent:
    raw = RawEvent(
        id=event.event_id or str(uuid.uuid4()),
        event_type=event.event_type,
        agent_id=event.agent_id,
        session_id=event.session_id,
        decision_id=event.decision_id,
        environment=event.environment,
        payload=event.payload,
        sdk_timestamp=event.sdk_timestamp,
        processed=False,
        correlation_id=event.correlation_id,
        framework=event.framework,
        regulations=event.regulations,
    )
    db.add(raw)
    await db.flush()
    return raw


async def store_event_batch(db: AsyncSession, events: list[EventCreate]) -> list[RawEvent]:
    raw_events = [
        RawEvent(
            id=event.event_id or str(uuid.uuid4()),
            event_type=event.event_type,
            agent_id=event.agent_id,
            session_id=event.session_id,
            decision_id=event.decision_id,
            environment=event.environment,
            payload=event.payload,
            sdk_timestamp=event.sdk_timestamp,
            processed=False,
            correlation_id=event.correlation_id,
            framework=event.framework,
            regulations=event.regulations,
        )
        for event in events
    ]
    db.add_all(raw_events)
    await db.commit()
    return raw_events


async def get_unprocessed_events(
    db: AsyncSession, limit: int = 100
) -> list[RawEvent]:
    result = await db.execute(
        select(RawEvent)
        .where(RawEvent.processed == False)  # noqa: E712
        .order_by(RawEvent.sdk_timestamp)
        .limit(limit)
    )
    return list(result.scalars().all())


async def mark_events_processed(db: AsyncSession, event_ids: list[str]) -> None:
    if not event_ids:
        return
    from sqlalchemy import update
    await db.execute(
        update(RawEvent)
        .where(RawEvent.id.in_(event_ids))
        .values(processed=True)
    )
    await db.flush()
