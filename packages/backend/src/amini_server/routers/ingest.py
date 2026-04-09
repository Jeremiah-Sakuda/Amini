import time
from collections import defaultdict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db, verify_api_key
from ..schemas.events import EventBatchCreate, EventCreate, EventResponse
from ..services.event_service import store_event, store_event_batch
from ..workers.processor import process_pending_events

router = APIRouter(
    prefix="/api/v1/events",
    tags=["events"],
    dependencies=[Depends(verify_api_key)],
)

# In-memory rate limiter: per API key, max 10 batch requests per 60-second window
_BATCH_RATE_LIMIT = 10
_BATCH_RATE_WINDOW = 60  # seconds
_batch_timestamps: dict[str, list[float]] = defaultdict(list)


def _check_batch_rate_limit(api_key: str) -> None:
    """Raise 429 if the API key has exceeded the batch rate limit."""
    now = time.monotonic()
    window_start = now - _BATCH_RATE_WINDOW
    # Prune old timestamps
    _batch_timestamps[api_key] = [
        ts for ts in _batch_timestamps[api_key] if ts > window_start
    ]
    if len(_batch_timestamps[api_key]) >= _BATCH_RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: max {_BATCH_RATE_LIMIT} batch requests per {_BATCH_RATE_WINDOW}s",
        )
    _batch_timestamps[api_key].append(now)


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
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    api_key = request.headers.get("authorization", "")
    _check_batch_rate_limit(api_key)
    raw_events = await store_event_batch(db, batch.events)
    background_tasks.add_task(_process_events)
    return {"accepted": len(raw_events)}


async def _process_events():
    from ..database import async_session_factory

    async with async_session_factory() as db:
        await process_pending_events(db)
