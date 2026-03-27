from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db
from ..schemas.sessions import SessionDetailResponse, SessionListResponse, SessionResponse
from ..services.session_service import get_session_detail, list_sessions

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.get("", response_model=SessionListResponse)
async def get_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    agent_id: str | None = None,
    environment: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    sessions, total = await list_sessions(
        db, page=page, page_size=page_size,
        agent_id=agent_id, environment=environment, status=status,
    )
    return SessionListResponse(
        sessions=[
            SessionResponse(
                id=s.id,
                session_external_id=s.session_external_id,
                agent_id=s.agent_id,
                environment=s.environment,
                status=s.status.value if hasattr(s.status, "value") else str(s.status),
                user_context=s.user_context,
                violation_count=len(s.violations) if s.violations else 0,
                decision_count=len(s.decisions) if s.decisions else 0,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in sessions
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    session = await get_session_detail(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionDetailResponse(
        id=session.id,
        session_external_id=session.session_external_id,
        agent_id=session.agent_id,
        environment=session.environment,
        status=session.status.value if hasattr(session.status, "value") else str(session.status),
        user_context=session.user_context,
        audit_metadata=session.audit_metadata,
        terminal_reason=session.terminal_reason,
        decisions=session.decisions,
        violations=session.violations,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )
