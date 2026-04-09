from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db, verify_api_key
from ..models.decision import DecisionNode
from ..models.session import AgentSession
from ..schemas.decisions import DecisionNodeResponse, DecisionTreeNode, DecisionTreeResponse

router = APIRouter(
    prefix="/api/v1/sessions/{session_id}/decisions",
    tags=["decisions"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("", response_model=list[DecisionNodeResponse])
async def get_decisions_flat(session_id: str, db: AsyncSession = Depends(get_db)):
    session = await db.execute(
        select(AgentSession).where(AgentSession.id == session_id)
    )
    if not session.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Session not found")

    result = await db.execute(
        select(DecisionNode)
        .where(DecisionNode.session_id == session_id)
        .order_by(DecisionNode.sequence_number)
    )
    decisions = result.scalars().all()
    return [DecisionNodeResponse.model_validate(d) for d in decisions]


@router.get("/tree", response_model=DecisionTreeResponse)
async def get_decisions_tree(session_id: str, db: AsyncSession = Depends(get_db)):
    session = await db.execute(
        select(AgentSession).where(AgentSession.id == session_id)
    )
    if not session.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Session not found")

    result = await db.execute(
        select(DecisionNode)
        .where(DecisionNode.session_id == session_id)
        .order_by(DecisionNode.sequence_number)
    )
    decisions = list(result.scalars().all())

    # Build tree structure
    by_id: dict[str, DecisionTreeNode] = {}
    roots: list[DecisionTreeNode] = []

    for d in decisions:
        node = DecisionTreeNode(
            id=d.id,
            decision_external_id=d.decision_external_id,
            decision_type=d.decision_type,
            sequence_number=d.sequence_number,
            parent_decision_id=d.parent_decision_id,
            action_type=d.action_type,
            duration_ms=d.duration_ms,
            has_error=d.has_error,
            policy_summary=d.policy_summary,
            input_context=d.input_context,
            reasoning_trace=d.reasoning_trace,
            action_detail=d.action_detail,
            output=d.output,
            created_at=d.created_at,
        )
        by_id[d.id] = node

    for d in decisions:
        node = by_id[d.id]
        if d.parent_decision_id and d.parent_decision_id in by_id:
            by_id[d.parent_decision_id].children.append(node)
        else:
            roots.append(node)

    return DecisionTreeResponse(session_id=session_id, roots=roots)
