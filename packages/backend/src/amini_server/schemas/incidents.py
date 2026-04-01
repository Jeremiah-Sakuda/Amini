from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class IncidentResponse(BaseModel):
    id: str
    title: str
    status: str
    severity: str
    violation_id: str
    session_id: str
    policy_name: str
    regulation: str | None = None
    regulation_article: str | None = None
    decision_chain_snapshot: dict | None = None
    affected_data_subjects: dict | None = None
    remediation_path: str = ""
    resolution_notes: str = ""
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IncidentListResponse(BaseModel):
    incidents: list[IncidentResponse]
    total: int


class IncidentUpdateRequest(BaseModel):
    status: str | None = None
    resolution_notes: str | None = None
    remediation_path: str | None = None
