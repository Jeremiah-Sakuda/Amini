from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db
from ..schemas.events import EventBatchCreate, EventCreate, EventResponse
from ..services.event_service import store_event, store_event_batch
from ..workers.processor import process_pending_events

router = APIRouter(prefix="/api/v1/events", tags=["events"])


@router.post("", status_code=202, response_model=EventResponse)
async def ingest_event(
    event: EventCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    raw = await store_event(db, event)
    await db.commit()
    background_tasks.add_task(_process_events)
    return EventResponse(event_id=raw.id)


@router.post("/batch", status_code=202)
async def ingest_event_batch(
    batch: EventBatchCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    raw_events = await store_event_batch(db, batch.events)
    background_tasks.add_task(_process_events)
    return {"accepted": len(raw_events)}


async def _process_events():
    from ..database import async_session_factory

    async with async_session_factory() as db:
        await process_pending_events(db)
