from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ReportGenerateRequest(BaseModel):
    framework: str
    period_start: str
    period_end: str
    agent_ids: list[str] | None = None
    title: str | None = None


class AuditReportResponse(BaseModel):
    id: str
    title: str
    report_type: str
    framework: str
    status: str
    period_start: str
    period_end: str
    agent_ids: list[str] | None = None
    summary: str = ""
    gap_analysis: dict | None = None
    content: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditReportListResponse(BaseModel):
    reports: list[AuditReportResponse]
    total: int
