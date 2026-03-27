from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..dependencies import get_db
from ..models.policy import Policy, PolicyVersion
from ..schemas.policies import (
    PolicyCreate,
    PolicyEvaluateRequest,
    PolicyResponse,
    PolicyVersionResponse,
)
from ..services.policy_engine import load_policy

router = APIRouter(prefix="/api/v1/policies", tags=["policies"])


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
    )
    db.add(version)
    await db.commit()

    return PolicyResponse(
        id=policy.id,
        name=policy.name,
        description=policy.description,
        is_active=policy.is_active,
        latest_version=PolicyVersionResponse(
            id=version.id,
            version_number=version.version_number,
            tier=version.tier.value if hasattr(version.tier, "value") else str(version.tier),
            enforcement=version.enforcement.value if hasattr(version.enforcement, "value") else str(version.enforcement),
            severity=version.severity,
            message=version.message,
            scope=version.scope,
            is_active=version.is_active,
            created_at=version.created_at,
        ),
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

    # Create new version
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
    )
    db.add(version)
    await db.commit()

    return PolicyResponse(
        id=policy.id,
        name=policy.name,
        description=policy.description,
        is_active=policy.is_active,
        latest_version=PolicyVersionResponse(
            id=version.id,
            version_number=version.version_number,
            tier=version.tier.value if hasattr(version.tier, "value") else str(version.tier),
            enforcement=version.enforcement.value if hasattr(version.enforcement, "value") else str(version.enforcement),
            severity=version.severity,
            message=version.message,
            scope=version.scope,
            is_active=version.is_active,
            created_at=version.created_at,
        ),
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


def _latest_version(versions: list[PolicyVersion]) -> PolicyVersionResponse | None:
    if not versions:
        return None
    latest = max(versions, key=lambda v: v.version_number)
    return PolicyVersionResponse(
        id=latest.id,
        version_number=latest.version_number,
        tier=latest.tier.value if hasattr(latest.tier, "value") else str(latest.tier),
        enforcement=latest.enforcement.value if hasattr(latest.enforcement, "value") else str(latest.enforcement),
        severity=latest.severity,
        message=latest.message,
        scope=latest.scope,
        is_active=latest.is_active,
        created_at=latest.created_at,
    )
