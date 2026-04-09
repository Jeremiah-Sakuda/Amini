import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db, verify_api_key
from ..schemas.reports import AuditReportListResponse, AuditReportResponse, ReportGenerateRequest
from ..services.report_service import (
    create_pending_report,
    generate_report_content,
    get_report,
    list_reports,
)

router = APIRouter(
    prefix="/api/v1/reports",
    tags=["audit-reports"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("", response_model=AuditReportResponse, status_code=202)
async def create_report(body: ReportGenerateRequest, db: AsyncSession = Depends(get_db)):
    report = await create_pending_report(
        db,
        framework=body.framework,
        period_start=body.period_start,
        period_end=body.period_end,
        agent_ids=body.agent_ids,
        title=body.title,
    )
    # Run generation in background — don't block the HTTP response
    asyncio.create_task(_generate_in_background(report.id, body))
    return _report_response(report)


async def _generate_in_background(report_id: str, body: ReportGenerateRequest) -> None:
    from ..database import async_session_factory

    async with async_session_factory() as db:
        await generate_report_content(
            db,
            report_id=report_id,
            framework=body.framework,
            period_start=body.period_start,
            period_end=body.period_end,
            agent_ids=body.agent_ids,
        )


@router.get("", response_model=AuditReportListResponse)
async def get_reports(
    framework: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    reports, total = await list_reports(db, framework=framework, page=page, page_size=page_size)
    return AuditReportListResponse(
        reports=[_report_response(r) for r in reports],
        total=total,
    )


@router.get("/{report_id}", response_model=AuditReportResponse)
async def get_report_detail(report_id: str, db: AsyncSession = Depends(get_db)):
    report = await get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return _report_response(report)


def _report_response(report) -> AuditReportResponse:
    return AuditReportResponse(
        id=report.id,
        title=report.title,
        report_type=report.report_type,
        framework=report.framework,
        status=report.status.value if hasattr(report.status, "value") else str(report.status),
        period_start=report.period_start,
        period_end=report.period_end,
        agent_ids=report.agent_ids,
        summary=report.summary,
        gap_analysis=report.gap_analysis,
        content=report.content,
        created_at=report.created_at,
    )
