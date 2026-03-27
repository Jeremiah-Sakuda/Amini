from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db
from ..schemas.violations import ViolationListResponse, ViolationResponse
from ..services.violation_service import list_violations

router = APIRouter(prefix="/api/v1/violations", tags=["violations"])


@router.get("", response_model=ViolationListResponse)
async def get_violations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session_id: str | None = None,
    severity: str | None = None,
    policy_version_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    violations, total = await list_violations(
        db,
        page=page,
        page_size=page_size,
        session_id=session_id,
        severity=severity,
        policy_version_id=policy_version_id,
    )
    return ViolationListResponse(
        violations=[ViolationResponse.model_validate(v) for v in violations],
        total=total,
        page=page,
        page_size=page_size,
    )
