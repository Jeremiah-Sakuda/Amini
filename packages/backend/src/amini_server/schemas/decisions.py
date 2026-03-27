from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DecisionNodeResponse(BaseModel):
    id: str
    decision_external_id: str
    decision_type: str
    sequence_number: int
    parent_decision_id: str | None = None
    action_type: str | None = None
    duration_ms: int | None = None
    has_error: bool = False
    policy_summary: dict | None = None
    input_context: dict | None = None
    reasoning_trace: str | None = None
    action_detail: dict | None = None
    output: dict | None = None
    side_effects: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DecisionTreeNode(BaseModel):
    id: str
    decision_external_id: str
    decision_type: str
    sequence_number: int
    parent_decision_id: str | None = None
    action_type: str | None = None
    duration_ms: int | None = None
    has_error: bool = False
    policy_summary: dict | None = None
    input_context: dict | None = None
    reasoning_trace: str | None = None
    action_detail: dict | None = None
    output: dict | None = None
    children: list[DecisionTreeNode] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class DecisionTreeResponse(BaseModel):
    session_id: str
    roots: list[DecisionTreeNode]
