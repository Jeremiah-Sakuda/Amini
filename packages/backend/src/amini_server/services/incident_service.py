from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.decision import DecisionNode
from ..models.incident import Incident, IncidentSeverity, IncidentStatus
from ..models.policy import PolicyVersion
from ..models.session import AgentSession
from ..models.violation import PolicyViolation


async def create_incident_from_violation(
    db: AsyncSession, violation: PolicyViolation
) -> Incident:
    """Auto-generate an incident package from a policy violation."""
    # Get session with decisions
    session_result = await db.execute(
        select(AgentSession)
        .options(selectinload(AgentSession.decisions))
        .where(AgentSession.id == violation.session_id)
    )
    session = session_result.scalar_one_or_none()

    # Get the policy version details
    policy_result = await db.execute(
        select(PolicyVersion).where(PolicyVersion.id == violation.policy_version_id)
    )
    policy_version = policy_result.scalar_one_or_none()

    # Build decision chain snapshot
    decision_chain = []
    if session:
        for d in sorted(session.decisions, key=lambda x: x.sequence_number):
            decision_chain.append({
                "id": d.id,
                "decision_type": d.decision_type,
                "action_type": d.action_type,
                "sequence_number": d.sequence_number,
                "has_error": d.has_error,
                "duration_ms": d.duration_ms,
            })

    severity_map = {
        "low": IncidentSeverity.LOW,
        "medium": IncidentSeverity.MEDIUM,
        "high": IncidentSeverity.HIGH,
        "critical": IncidentSeverity.CRITICAL,
    }

    incident = Incident(
        title=f"Policy violation: {violation.violation_type}",
        severity=severity_map.get(
            violation.severity.value if hasattr(violation.severity, "value") else violation.severity,
            IncidentSeverity.MEDIUM,
        ),
        violation_id=violation.id,
        session_id=violation.session_id,
        policy_name=policy_version.policy.name if policy_version and hasattr(policy_version, "policy") else "",
        regulation=policy_version.regulation if policy_version else None,
        regulation_article=policy_version.regulation_article if policy_version else None,
        decision_chain_snapshot={"decisions": decision_chain},
        remediation_path=_generate_remediation(violation, policy_version),
    )
    db.add(incident)
    await db.flush()
    return incident


async def list_incidents(
    db: AsyncSession,
    status: str | None = None,
    severity: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Incident], int]:
    query = select(Incident)
    count_query = select(func.count()).select_from(Incident)

    if status:
        query = query.where(Incident.status == IncidentStatus(status))
        count_query = count_query.where(Incident.status == IncidentStatus(status))
    if severity:
        query = query.where(Incident.severity == IncidentSeverity(severity))
        count_query = count_query.where(Incident.severity == IncidentSeverity(severity))

    query = query.order_by(Incident.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    incidents = list(result.scalars().all())

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    return incidents, total


async def get_incident(db: AsyncSession, incident_id: str) -> Incident | None:
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id)
    )
    return result.scalar_one_or_none()


async def update_incident(
    db: AsyncSession,
    incident_id: str,
    updates: dict,
) -> Incident | None:
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()
    if incident is None:
        return None

    if "status" in updates and updates["status"]:
        incident.status = IncidentStatus(updates["status"])
    if "resolution_notes" in updates and updates["resolution_notes"] is not None:
        incident.resolution_notes = updates["resolution_notes"]
    if "remediation_path" in updates and updates["remediation_path"] is not None:
        incident.remediation_path = updates["remediation_path"]

    await db.flush()
    await db.commit()
    return incident


def _generate_remediation(
    violation: PolicyViolation,
    policy_version: PolicyVersion | None,
) -> str:
    parts = [f"1. Review the policy violation: {violation.description}"]

    if policy_version and policy_version.regulation:
        parts.append(
            f"2. Check compliance with {policy_version.regulation} "
            f"Article {policy_version.regulation_article or 'N/A'}"
        )

    severity = violation.severity.value if hasattr(violation.severity, "value") else violation.severity
    if severity in ("critical", "high"):
        parts.append("3. Escalate to compliance team immediately")
        parts.append("4. Document remediation steps taken")
        parts.append("5. Update policy rules if the violation indicates a gap")
    else:
        parts.append("3. Assess whether agent behavior needs adjustment")
        parts.append("4. Update policy scope or rules as needed")

    return "\n".join(parts)
