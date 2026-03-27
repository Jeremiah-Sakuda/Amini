from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.violation import PolicyViolation, ViolationSeverity


async def record_violation(
    db: AsyncSession,
    session_id: str,
    policy_version_id: str,
    severity: str,
    violation_type: str,
    description: str,
    decision_node_id: str | None = None,
    evidence: dict | None = None,
) -> PolicyViolation:
    violation = PolicyViolation(
        session_id=session_id,
        decision_node_id=decision_node_id,
        policy_version_id=policy_version_id,
        severity=ViolationSeverity(severity),
        violation_type=violation_type,
        description=description,
        evidence=evidence,
    )
    db.add(violation)
    await db.flush()
    return violation


async def list_violations(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    session_id: str | None = None,
    severity: str | None = None,
    policy_version_id: str | None = None,
) -> tuple[list[PolicyViolation], int]:
    query = select(PolicyViolation)
    count_query = select(func.count()).select_from(PolicyViolation)

    if session_id:
        query = query.where(PolicyViolation.session_id == session_id)
        count_query = count_query.where(PolicyViolation.session_id == session_id)

    if severity:
        query = query.where(PolicyViolation.severity == ViolationSeverity(severity))
        count_query = count_query.where(
            PolicyViolation.severity == ViolationSeverity(severity)
        )

    if policy_version_id:
        query = query.where(PolicyViolation.policy_version_id == policy_version_id)
        count_query = count_query.where(
            PolicyViolation.policy_version_id == policy_version_id
        )

    query = query.order_by(PolicyViolation.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    violations = list(result.scalars().all())

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    return violations, total
