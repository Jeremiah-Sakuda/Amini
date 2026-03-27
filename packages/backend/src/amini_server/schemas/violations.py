from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ViolationResponse(BaseModel):
    id: str
    session_id: str
    decision_node_id: str | None = None
    policy_version_id: str
    severity: str
    violation_type: str
    description: str
    evidence: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ViolationListResponse(BaseModel):
    violations: list[ViolationResponse]
    total: int
    page: int
    page_size: int
