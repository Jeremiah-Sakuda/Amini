from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class PolicyCreate(BaseModel):
    name: str
    description: str = ""
    yaml_content: str
    tier: str = "deterministic"
    enforcement: str = "log_only"
    severity: str = "medium"
    scope: dict | None = None


class PolicyResponse(BaseModel):
    id: str
    name: str
    description: str
    is_active: bool
    latest_version: PolicyVersionResponse | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PolicyVersionResponse(BaseModel):
    id: str
    version_number: int
    tier: str
    enforcement: str
    severity: str
    message: str
    scope: dict | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PolicyEvaluateRequest(BaseModel):
    session_ids: list[str] | None = None
    dry_run: bool = False
