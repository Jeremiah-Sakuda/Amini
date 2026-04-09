from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..dependencies import get_db, verify_api_key
from ..models.policy import Policy, PolicyVersion
from ..schemas.policies import (
    PolicyCreate,
    PolicyEvaluateRequest,
    PolicyResponse,
    PolicyVersionResponse,
)
from ..services.policy_engine import load_policy

router = APIRouter(
    prefix="/api/v1/policies",
    tags=["policies"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("", response_model=list[PolicyResponse])
async def list_policies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Policy).options(selectinload(Policy.versions))
    )
    policies = result.scalars().unique().all()

    return [
        PolicyResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            is_active=p.is_active,
            latest_version=_latest_version(p.versions),
            created_at=p.created_at,
        )
        for p in policies
    ]


@router.post("", response_model=PolicyResponse, status_code=201)
async def create_policy(body: PolicyCreate, db: AsyncSession = Depends(get_db)):
    parsed = load_policy(body.yaml_content)

    policy = Policy(name=body.name, description=body.description, is_active=True)
    db.add(policy)
    await db.flush()

    version = PolicyVersion(
        policy_id=policy.id,
        version_number=1,
        yaml_content=body.yaml_content,
        parsed_rule=parsed,
        scope=body.scope or parsed.get("scope"),
        tier=body.tier,
        enforcement=body.enforcement,
        severity=body.severity,
        message=parsed.get("message", ""),
        is_active=True,
        regulation=body.regulation,
        regulation_article=body.regulation_article,
        risk_class=body.risk_class,
        agent_tags=body.agent_tags,
        effective_date=body.effective_date,
        human_review_required=body.human_review_required,
        max_autonomous_actions=body.max_autonomous_actions,
    )
    db.add(version)
    await db.commit()

    return PolicyResponse(
        id=policy.id,
        name=policy.name,
        description=policy.description,
        is_active=policy.is_active,
        latest_version=_version_response(version),
        created_at=policy.created_at,
    )


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(policy_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Policy)
        .options(selectinload(Policy.versions))
        .where(Policy.id == policy_id)
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    return PolicyResponse(
        id=policy.id,
        name=policy.name,
        description=policy.description,
        is_active=policy.is_active,
        latest_version=_latest_version(policy.versions),
        created_at=policy.created_at,
    )


@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: str, body: PolicyCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Policy)
        .options(selectinload(Policy.versions))
        .where(Policy.id == policy_id)
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    parsed = load_policy(body.yaml_content)
    policy.description = body.description

    max_version = max((v.version_number for v in policy.versions), default=0)
    version = PolicyVersion(
        policy_id=policy.id,
        version_number=max_version + 1,
        yaml_content=body.yaml_content,
        parsed_rule=parsed,
        scope=body.scope or parsed.get("scope"),
        tier=body.tier,
        enforcement=body.enforcement,
        severity=body.severity,
        message=parsed.get("message", ""),
        is_active=True,
        regulation=body.regulation,
        regulation_article=body.regulation_article,
        risk_class=body.risk_class,
        agent_tags=body.agent_tags,
        effective_date=body.effective_date,
        human_review_required=body.human_review_required,
        max_autonomous_actions=body.max_autonomous_actions,
    )
    db.add(version)
    await db.commit()

    return PolicyResponse(
        id=policy.id,
        name=policy.name,
        description=policy.description,
        is_active=policy.is_active,
        latest_version=_version_response(version),
        created_at=policy.created_at,
    )


@router.post("/{policy_id}/evaluate")
async def evaluate_policy(
    policy_id: str,
    body: PolicyEvaluateRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Policy).where(Policy.id == policy_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Policy not found")

    return {"status": "evaluation_queued", "policy_id": policy_id}


def _version_response(v: PolicyVersion) -> PolicyVersionResponse:
    return PolicyVersionResponse(
        id=v.id,
        version_number=v.version_number,
        tier=v.tier.value if hasattr(v.tier, "value") else str(v.tier),
        enforcement=v.enforcement.value if hasattr(v.enforcement, "value") else str(v.enforcement),
        severity=v.severity,
        message=v.message,
        scope=v.scope,
        is_active=v.is_active,
        regulation=v.regulation,
        regulation_article=v.regulation_article,
        risk_class=v.risk_class,
        agent_tags=v.agent_tags,
        effective_date=v.effective_date,
        human_review_required=v.human_review_required,
        max_autonomous_actions=v.max_autonomous_actions,
        created_at=v.created_at,
    )


def _latest_version(versions: list[PolicyVersion]) -> PolicyVersionResponse | None:
    if not versions:
        return None
    latest = max(versions, key=lambda v: v.version_number)
    return _version_response(latest)
