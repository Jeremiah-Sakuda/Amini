from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AgentRegistryEntry(BaseModel):
    id: str
    agent_external_id: str
    name: str
    description: str | None = None
    framework: str = ""
    provider: str = ""
    risk_class: str = ""
    tags: list[str] | None = None
    data_access_patterns: dict | None = None
    deployment_status: str = "active"
    discovery_method: str = "sdk"
    regulations: list[str] | None = None
    session_count: int = 0
    violation_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentRegistryListResponse(BaseModel):
    agents: list[AgentRegistryEntry]
    total: int


class AgentRegistryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    framework: str | None = None
    provider: str | None = None
    risk_class: str | None = None
    tags: list[str] | None = None
    data_access_patterns: dict | None = None
    deployment_status: str | None = None
    regulations: list[str] | None = None
