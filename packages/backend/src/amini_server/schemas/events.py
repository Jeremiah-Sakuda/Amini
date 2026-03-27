from __future__ import annotations

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    event_id: str | None = None
    event_type: str
    agent_id: str
    session_id: str
    decision_id: str | None = None
    environment: str = "development"
    payload: dict | None = None
    sdk_timestamp: float


class EventBatchCreate(BaseModel):
    events: list[EventCreate] = Field(min_length=1, max_length=500)


class EventResponse(BaseModel):
    event_id: str
    status: str = "accepted"

    model_config = {"from_attributes": True}
