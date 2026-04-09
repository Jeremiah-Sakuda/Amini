from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.audit_report import AuditReport, ReportStatus
from ..models.incident import Incident
from ..models.policy import PolicyVersion
from ..models.session import AgentSession
from ..models.violation import PolicyViolation


async def generate_report(
    db: AsyncSession,
    framework: str,
    period_start: str,
    period_end: str,
    agent_ids: list[str] | None = None,
    title: str | None = None,
) -> AuditReport:
    report_title = title or f"{framework.upper()} Compliance Report ({period_start} to {period_end})"
    report = AuditReport(
        title=report_title,
        report_type="compliance",
        framework=framework,
        status=ReportStatus.GENERATING,
        period_start=period_start,
        period_end=period_end,
        agent_ids=agent_ids,
    )
    db.add(report)
    await db.flush()

    try:
        content = await _build_report_content(db, framework, period_start, period_end, agent_ids)
        report.content = content
        report.summary = content.get("executive_summary", "")
        report.gap_analysis = content.get("gap_analysis", {})
        report.status = ReportStatus.COMPLETED
    except Exception as e:
        report.status = ReportStatus.FAILED
        report.summary = f"Report generation failed: {str(e)}"

    await db.flush()
    await db.commit()
    return report


async def _build_report_content(
    db: AsyncSession,
    framework: str,
    period_start: str,
    period_end: str,
    agent_ids: list[str] | None,
) -> dict:
    # Query sessions in the period
    session_query = select(AgentSession).where(
        AgentSession.created_at >= period_start,
        AgentSession.created_at <= period_end,
    )
    if agent_ids:
        session_query = session_query.where(AgentSession.agent_id.in_(agent_ids))

    session_result = await db.execute(
        session_query.options(
            selectinload(AgentSession.decisions),
            selectinload(AgentSession.violations),
        )
    )
    sessions = list(session_result.scalars().unique().all())

    # Aggregate stats
    total_sessions = len(sessions)
    total_decisions = sum(len(s.decisions) for s in sessions)
    total_violations = sum(len(s.violations) for s in sessions)
    sessions_with_violations = sum(1 for s in sessions if s.violations)
    error_sessions = sum(1 for s in sessions if s.status.value == "error")

    # Violation breakdown
    violation_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for s in sessions:
        for v in s.violations:
            sev = v.severity.value if hasattr(v.severity, "value") else v.severity
            if sev in violation_by_severity:
                violation_by_severity[sev] += 1

    # Incident count in period
    incident_result = await db.execute(
        select(func.count()).select_from(Incident).where(
            Incident.created_at >= period_start,
            Incident.created_at <= period_end,
        )
    )
    total_incidents = incident_result.scalar() or 0

    # Policy coverage
    policy_result = await db.execute(
        select(PolicyVersion).where(PolicyVersion.is_active == True)  # noqa: E712
    )
    active_policies = list(policy_result.scalars().all())
    policies_with_regulation = [p for p in active_policies if p.regulation]

    content = {
        "executive_summary": _build_executive_summary(
            framework, period_start, period_end,
            total_sessions, total_violations, total_incidents,
        ),
        "report_metadata": {
            "framework": framework,
            "period_start": period_start,
            "period_end": period_end,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "agent_count": len(set(s.agent_id for s in sessions)),
        },
        "session_summary": {
            "total_sessions": total_sessions,
            "total_decisions": total_decisions,
            "error_sessions": error_sessions,
            "sessions_with_violations": sessions_with_violations,
        },
        "violation_summary": {
            "total_violations": total_violations,
            "by_severity": violation_by_severity,
        },
        "incident_summary": {
            "total_incidents": total_incidents,
        },
        "policy_coverage": {
            "total_active_policies": len(active_policies),
            "policies_linked_to_regulation": len(policies_with_regulation),
            "framework_policies": [
                {
                    "name": p.policy.name if hasattr(p, "policy") and p.policy else "unknown",
                    "regulation": p.regulation,
                    "article": p.regulation_article,
                    "enforcement": p.enforcement.value if hasattr(p.enforcement, "value") else p.enforcement,
                }
                for p in policies_with_regulation
                if p.regulation and p.regulation.lower().replace(" ", "-") == framework.lower().replace(" ", "-")
            ],
        },
        "evidence_log": {
            "decision_chains_captured": total_decisions,
            "policy_evaluations_performed": total_sessions * len(active_policies),
            "violations_detected": total_violations,
            "human_review_records": 0,
        },
        "gap_analysis": {
            "missing_policies": _identify_gaps(framework, active_policies),
        },
    }

    return content


def _build_executive_summary(
    framework: str,
    period_start: str,
    period_end: str,
    total_sessions: int,
    total_violations: int,
    total_incidents: int,
) -> str:
    return (
        f"This report covers AI agent activity from {period_start} to {period_end} "
        f"under the {framework} compliance framework. "
        f"During this period, {total_sessions} agent sessions were recorded, "
        f"resulting in {total_violations} policy violations and {total_incidents} incidents. "
        f"All decision chains have been captured and are available for audit review."
    )


def _identify_gaps(framework: str, active_policies: list) -> list[str]:
    gaps = []
    framework_lower = framework.lower().replace(" ", "-")

    linked_articles = set()
    for p in active_policies:
        if p.regulation and p.regulation.lower().replace(" ", "-") == framework_lower:
            if p.regulation_article:
                linked_articles.add(p.regulation_article)

    if framework_lower == "eu-ai-act":
        required = {"6", "9", "10", "12", "13", "14", "15", "26"}
        missing = required - linked_articles
        for article in sorted(missing):
            gaps.append(f"No policy mapped to EU AI Act Article {article}")
    elif framework_lower == "soc2":
        required = {"CC6.1", "CC6.6", "CC7.2", "CC7.3", "CC8.1", "A1.2"}
        missing = required - linked_articles
        for article in sorted(missing):
            gaps.append(f"No policy mapped to SOC 2 {article}")

    return gaps


async def list_reports(
    db: AsyncSession,
    framework: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[AuditReport], int]:
    query = select(AuditReport)
    count_query = select(func.count()).select_from(AuditReport)

    if framework:
        query = query.where(AuditReport.framework == framework)
        count_query = count_query.where(AuditReport.framework == framework)

    query = query.order_by(AuditReport.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    reports = list(result.scalars().all())

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    return reports, total


async def get_report(db: AsyncSession, report_id: str) -> AuditReport | None:
    result = await db.execute(
        select(AuditReport).where(AuditReport.id == report_id)
    )
    return result.scalar_one_or_none()
