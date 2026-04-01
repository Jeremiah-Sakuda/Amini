from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db
from ..schemas.regulations import (
    ComplianceOverviewResponse,
    RegulationListResponse,
    RegulationResponse,
    RegulatoryRequirementResponse,
)
from ..services.regulation_service import (
    get_compliance_overview,
    get_regulation,
    get_regulation_by_code,
    list_regulations,
    seed_regulations,
)

router = APIRouter(prefix="/api/v1/regulations", tags=["regulations"])


@router.get("", response_model=RegulationListResponse)
async def get_regulations(db: AsyncSession = Depends(get_db)):
    regulations, total = await list_regulations(db)
    return RegulationListResponse(
        regulations=[
            RegulationResponse(
                id=r.id,
                name=r.name,
                short_code=r.short_code,
                version=r.version,
                jurisdiction=r.jurisdiction,
                description=r.description,
                effective_date=r.effective_date,
                is_active=r.is_active,
                requirements=[
                    RegulatoryRequirementResponse(
                        id=req.id,
                        article=req.article,
                        section=req.section,
                        title=req.title,
                        description=req.description,
                        evidence_types=req.evidence_types,
                        applies_to_risk_class=req.applies_to_risk_class,
                        review_cadence_days=req.review_cadence_days,
                    )
                    for req in r.requirements
                ],
                created_at=r.created_at,
            )
            for r in regulations
        ],
        total=total,
    )


@router.get("/{regulation_id}", response_model=RegulationResponse)
async def get_regulation_detail(regulation_id: str, db: AsyncSession = Depends(get_db)):
    regulation = await get_regulation(db, regulation_id)
    if not regulation:
        raise HTTPException(status_code=404, detail="Regulation not found")
    return RegulationResponse(
        id=regulation.id,
        name=regulation.name,
        short_code=regulation.short_code,
        version=regulation.version,
        jurisdiction=regulation.jurisdiction,
        description=regulation.description,
        effective_date=regulation.effective_date,
        is_active=regulation.is_active,
        requirements=[
            RegulatoryRequirementResponse(
                id=req.id,
                article=req.article,
                section=req.section,
                title=req.title,
                description=req.description,
                evidence_types=req.evidence_types,
                applies_to_risk_class=req.applies_to_risk_class,
                review_cadence_days=req.review_cadence_days,
            )
            for req in regulation.requirements
        ],
        created_at=regulation.created_at,
    )


@router.post("/seed", status_code=201)
async def seed_regulation_templates(db: AsyncSession = Depends(get_db)):
    created = await seed_regulations(db)
    return {"seeded": len(created), "regulations": [r.short_code for r in created]}


@router.get("/compliance/{agent_id}", response_model=ComplianceOverviewResponse)
async def get_agent_compliance(agent_id: str, db: AsyncSession = Depends(get_db)):
    overview = await get_compliance_overview(db, agent_id)
    if not overview:
        raise HTTPException(status_code=404, detail="Agent not found")
    return ComplianceOverviewResponse(**overview)
