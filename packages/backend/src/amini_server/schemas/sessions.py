from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from .decisions import DecisionNodeResponse
from .violations import ViolationResponse


class SessionResponse(BaseModel):
    id: str
    session_external_id: str
    agent_id: str
    environment: str
    status: str
    user_context: dict | None = None
    violation_count: int = 0
    decision_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]
    total: int
    page: int
    page_size: int


class SessionDetailResponse(BaseModel):
    id: str
    session_external_id: str
    agent_id: str
    environment: str
    status: str
    user_context: dict | None = None
    audit_metadata: dict | None = None
    terminal_reason: str | None = None
    decisions: list[DecisionNodeResponse] = []
    violations: list[ViolationResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
