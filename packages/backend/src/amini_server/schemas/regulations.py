from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class RegulatoryRequirementResponse(BaseModel):
    id: str
    article: str
    section: str
    title: str
    description: str
    evidence_types: dict | None = None
    applies_to_risk_class: str | None = None
    review_cadence_days: int = 90

    model_config = {"from_attributes": True}


class RegulationResponse(BaseModel):
    id: str
    name: str
    short_code: str
    version: str
    jurisdiction: str
    description: str
    effective_date: str | None = None
    is_active: bool
    requirements: list[RegulatoryRequirementResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class RegulationListResponse(BaseModel):
    regulations: list[RegulationResponse]
    total: int


class ComplianceMappingResponse(BaseModel):
    id: str
    agent_id: str
    requirement_id: str
    requirement_article: str = ""
    requirement_title: str = ""
    regulation_name: str = ""
    status: str
    evidence: dict | None = None
    notes: str = ""
    last_reviewed: str | None = None
    next_review_due: str | None = None

    model_config = {"from_attributes": True}


class ComplianceGapResponse(BaseModel):
    regulation: str
    total_requirements: int
    assessed: int
    compliant: int
    non_compliant: int
    partially_compliant: int
    not_assessed: int
    compliance_percentage: float
    gaps: list[ComplianceMappingResponse] = []


class ComplianceOverviewResponse(BaseModel):
    agent_id: str
    agent_name: str
    regulations: list[ComplianceGapResponse] = []
