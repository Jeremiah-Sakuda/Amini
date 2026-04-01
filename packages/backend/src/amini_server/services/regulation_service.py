from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.agent import Agent
from ..models.regulation import (
    ComplianceMapping,
    ComplianceStatus,
    Regulation,
    RegulatoryRequirement,
)

# --- Pre-built regulatory templates ---

EU_AI_ACT_REQUIREMENTS = [
    {
        "article": "6",
        "section": "Classification",
        "title": "Classification rules for high-risk AI systems",
        "description": "AI systems must be classified according to their risk level. High-risk systems require conformity assessment.",
        "evidence_types": {"required": ["risk_assessment", "system_classification"]},
        "applies_to_risk_class": "high",
    },
    {
        "article": "9",
        "section": "Risk Management",
        "title": "Risk management system",
        "description": "A risk management system shall be established, implemented, documented and maintained for high-risk AI systems.",
        "evidence_types": {"required": ["risk_management_plan", "risk_assessment_report"]},
        "applies_to_risk_class": "high",
    },
    {
        "article": "10",
        "section": "Data Governance",
        "title": "Data and data governance",
        "description": "Training, validation and testing data sets shall be subject to appropriate data governance and management practices.",
        "evidence_types": {"required": ["data_governance_policy", "data_quality_report"]},
        "applies_to_risk_class": "high",
    },
    {
        "article": "12",
        "section": "Record-keeping",
        "title": "Record-keeping",
        "description": "High-risk AI systems shall technically allow for automatic recording of events (logs) over their lifetime.",
        "evidence_types": {"required": ["audit_logs", "event_records", "decision_traces"]},
        "applies_to_risk_class": "high",
    },
    {
        "article": "13",
        "section": "Transparency",
        "title": "Transparency and provision of information to deployers",
        "description": "High-risk AI systems shall be designed and developed to ensure their operation is sufficiently transparent.",
        "evidence_types": {"required": ["system_documentation", "user_instructions"]},
        "applies_to_risk_class": "high",
    },
    {
        "article": "14",
        "section": "Human Oversight",
        "title": "Human oversight",
        "description": "High-risk AI systems shall be designed to be effectively overseen by natural persons during their period of use.",
        "evidence_types": {"required": ["human_oversight_protocol", "escalation_records", "review_logs"]},
        "applies_to_risk_class": "high",
        "review_cadence_days": 30,
    },
    {
        "article": "15",
        "section": "Accuracy & Robustness",
        "title": "Accuracy, robustness and cybersecurity",
        "description": "High-risk AI systems shall be designed and developed to achieve an appropriate level of accuracy, robustness and cybersecurity.",
        "evidence_types": {"required": ["accuracy_metrics", "robustness_testing", "security_assessment"]},
        "applies_to_risk_class": "high",
    },
    {
        "article": "26",
        "section": "Deployer Obligations",
        "title": "Obligations of deployers of high-risk AI systems",
        "description": "Deployers shall implement appropriate technical and organisational measures to ensure they use high-risk AI systems in accordance with instructions.",
        "evidence_types": {"required": ["usage_policy", "compliance_training_records"]},
        "applies_to_risk_class": "high",
    },
]

SOC2_REQUIREMENTS = [
    {
        "article": "CC6.1",
        "section": "Logical Access",
        "title": "Logical and physical access controls",
        "description": "The entity implements logical access security measures to protect against unauthorized access.",
        "evidence_types": {"required": ["access_control_logs", "authentication_records"]},
    },
    {
        "article": "CC6.6",
        "section": "System Boundaries",
        "title": "Restriction of system access at boundaries",
        "description": "The entity restricts the ability of users to access systems through system boundaries including network segmentation.",
        "evidence_types": {"required": ["network_policies", "boundary_controls"]},
    },
    {
        "article": "CC7.2",
        "section": "Monitoring",
        "title": "Monitoring of system components",
        "description": "The entity monitors system components and anomalies indicative of malicious acts, natural disasters, and errors.",
        "evidence_types": {"required": ["monitoring_logs", "alert_records", "anomaly_reports"]},
        "review_cadence_days": 30,
    },
    {
        "article": "CC7.3",
        "section": "Change Detection",
        "title": "Detection of unauthorized changes",
        "description": "The entity evaluates detected security events and determines if they could represent incidents.",
        "evidence_types": {"required": ["incident_logs", "change_detection_reports"]},
    },
    {
        "article": "CC8.1",
        "section": "Change Management",
        "title": "Changes to infrastructure and software",
        "description": "The entity authorizes, designs, develops, configures, documents, tests, approves, and implements changes.",
        "evidence_types": {"required": ["change_records", "approval_logs", "test_results"]},
    },
    {
        "article": "A1.2",
        "section": "Availability",
        "title": "Environmental protections and recovery",
        "description": "The entity authorizes, designs, develops or acquires, implements, operates, approves, maintains, and monitors environmental protections.",
        "evidence_types": {"required": ["uptime_records", "recovery_plans"]},
        "review_cadence_days": 90,
    },
]


async def seed_regulations(db: AsyncSession) -> list[Regulation]:
    """Seed the database with pre-built regulatory templates."""
    created = []

    for reg_data in [
        {
            "name": "EU AI Act",
            "short_code": "eu-ai-act",
            "version": "2024",
            "jurisdiction": "European Union",
            "description": "Regulation laying down harmonised rules on artificial intelligence.",
            "effective_date": "2026-08-01",
            "requirements": EU_AI_ACT_REQUIREMENTS,
        },
        {
            "name": "SOC 2 Type II",
            "short_code": "soc2",
            "version": "2024",
            "jurisdiction": "United States",
            "description": "Service Organization Control 2 — Trust Services Criteria for Security, Availability, Processing Integrity, Confidentiality, and Privacy.",
            "effective_date": "2024-01-01",
            "requirements": SOC2_REQUIREMENTS,
        },
    ]:
        existing = await db.execute(
            select(Regulation).where(Regulation.short_code == reg_data["short_code"])
        )
        if existing.scalar_one_or_none():
            continue

        requirements = reg_data.pop("requirements")
        regulation = Regulation(**reg_data)
        db.add(regulation)
        await db.flush()

        for req_data in requirements:
            req = RegulatoryRequirement(
                regulation_id=regulation.id,
                **req_data,
            )
            db.add(req)

        await db.flush()
        created.append(regulation)

    if created:
        await db.commit()
    return created


async def list_regulations(db: AsyncSession) -> tuple[list[Regulation], int]:
    result = await db.execute(
        select(Regulation)
        .options(selectinload(Regulation.requirements))
        .order_by(Regulation.name)
    )
    regulations = list(result.scalars().unique().all())
    return regulations, len(regulations)


async def get_regulation(db: AsyncSession, regulation_id: str) -> Regulation | None:
    result = await db.execute(
        select(Regulation)
        .options(selectinload(Regulation.requirements))
        .where(Regulation.id == regulation_id)
    )
    return result.scalar_one_or_none()


async def get_regulation_by_code(db: AsyncSession, short_code: str) -> Regulation | None:
    result = await db.execute(
        select(Regulation)
        .options(selectinload(Regulation.requirements))
        .where(Regulation.short_code == short_code)
    )
    return result.scalar_one_or_none()


async def get_compliance_overview(
    db: AsyncSession, agent_id: str
) -> dict:
    agent_result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = agent_result.scalar_one_or_none()
    if agent is None:
        return {}

    regulations, _ = await list_regulations(db)
    overview = {
        "agent_id": agent.id,
        "agent_name": agent.name,
        "regulations": [],
    }

    for regulation in regulations:
        gap_data = {
            "regulation": regulation.name,
            "total_requirements": len(regulation.requirements),
            "assessed": 0,
            "compliant": 0,
            "non_compliant": 0,
            "partially_compliant": 0,
            "not_assessed": 0,
            "compliance_percentage": 0.0,
            "gaps": [],
        }

        for req in regulation.requirements:
            mapping_result = await db.execute(
                select(ComplianceMapping).where(
                    ComplianceMapping.agent_id == agent_id,
                    ComplianceMapping.requirement_id == req.id,
                )
            )
            mapping = mapping_result.scalar_one_or_none()

            if mapping is None:
                gap_data["not_assessed"] += 1
                gap_data["gaps"].append({
                    "id": "",
                    "agent_id": agent_id,
                    "requirement_id": req.id,
                    "requirement_article": req.article,
                    "requirement_title": req.title,
                    "regulation_name": regulation.name,
                    "status": "not_assessed",
                    "evidence": None,
                    "notes": "",
                    "last_reviewed": None,
                    "next_review_due": None,
                })
            else:
                gap_data["assessed"] += 1
                status = mapping.status.value if hasattr(mapping.status, "value") else mapping.status
                if status == "compliant":
                    gap_data["compliant"] += 1
                elif status == "non_compliant":
                    gap_data["non_compliant"] += 1
                    gap_data["gaps"].append({
                        "id": mapping.id,
                        "agent_id": agent_id,
                        "requirement_id": req.id,
                        "requirement_article": req.article,
                        "requirement_title": req.title,
                        "regulation_name": regulation.name,
                        "status": status,
                        "evidence": mapping.evidence,
                        "notes": mapping.notes,
                        "last_reviewed": mapping.last_reviewed,
                        "next_review_due": mapping.next_review_due,
                    })
                elif status == "partially_compliant":
                    gap_data["partially_compliant"] += 1
                    gap_data["gaps"].append({
                        "id": mapping.id,
                        "agent_id": agent_id,
                        "requirement_id": req.id,
                        "requirement_article": req.article,
                        "requirement_title": req.title,
                        "regulation_name": regulation.name,
                        "status": status,
                        "evidence": mapping.evidence,
                        "notes": mapping.notes,
                        "last_reviewed": mapping.last_reviewed,
                        "next_review_due": mapping.next_review_due,
                    })

        total = gap_data["total_requirements"]
        if total > 0:
            gap_data["compliance_percentage"] = round(
                (gap_data["compliant"] / total) * 100, 1
            )

        overview["regulations"].append(gap_data)

    return overview
