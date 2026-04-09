from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db, verify_api_key
from ..schemas.reports import AuditReportListResponse, AuditReportResponse, ReportGenerateRequest
from ..services.report_service import generate_report, get_report, list_reports

router = APIRouter(
    prefix="/api/v1/reports",
    tags=["audit-reports"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("", response_model=AuditReportResponse, status_code=201)
async def create_report(body: ReportGenerateRequest, db: AsyncSession = Depends(get_db)):
    report = await generate_report(
        db,
        framework=body.framework,
        period_start=body.period_start,
        period_end=body.period_end,
        agent_ids=body.agent_ids,
        title=body.title,
    )
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


@router.get("", response_model=AuditReportListResponse)
async def get_reports(
    framework: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    reports, total = await list_reports(db, framework=framework, page=page, page_size=page_size)
    return AuditReportListResponse(
        reports=[
            AuditReportResponse(
                id=r.id,
                title=r.title,
                report_type=r.report_type,
                framework=r.framework,
                status=r.status.value if hasattr(r.status, "value") else str(r.status),
                period_start=r.period_start,
                period_end=r.period_end,
                agent_ids=r.agent_ids,
                summary=r.summary,
                gap_analysis=r.gap_analysis,
                content=r.content,
                created_at=r.created_at,
            )
            for r in reports
        ],
        total=total,
    )


@router.get("/{report_id}", response_model=AuditReportResponse)
async def get_report_detail(report_id: str, db: AsyncSession = Depends(get_db)):
    report = await get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
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
