from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db
from ..services.retention_service import cleanup_expired_data

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/ready")
async def ready():
    return {"status": "ready"}


@router.post("/api/v1/admin/cleanup")
async def run_retention_cleanup(db: AsyncSession = Depends(get_db)):
    """Trigger data retention cleanup — deletes records older than retention_days."""
    result = await cleanup_expired_data(db)
    return {"status": "completed", "deleted": result}
