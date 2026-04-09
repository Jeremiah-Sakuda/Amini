from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db, verify_api_key
from ..schemas.incidents import IncidentListResponse, IncidentResponse, IncidentUpdateRequest
from ..services.incident_service import get_incident, list_incidents, update_incident

router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["incidents"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("", response_model=IncidentListResponse)
async def get_incidents(
    status: str | None = None,
    severity: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    incidents, total = await list_incidents(
        db, status=status, severity=severity, page=page, page_size=page_size
    )
    return IncidentListResponse(
        incidents=[
            IncidentResponse(
                id=i.id,
                title=i.title,
                status=i.status.value if hasattr(i.status, "value") else str(i.status),
                severity=i.severity.value if hasattr(i.severity, "value") else str(i.severity),
                violation_id=i.violation_id,
                session_id=i.session_id,
                policy_name=i.policy_name,
                regulation=i.regulation,
                regulation_article=i.regulation_article,
                decision_chain_snapshot=i.decision_chain_snapshot,
                affected_data_subjects=i.affected_data_subjects,
                remediation_path=i.remediation_path,
                resolution_notes=i.resolution_notes,
                created_at=i.created_at,
                updated_at=i.updated_at,
            )
            for i in incidents
        ],
        total=total,
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident_detail(incident_id: str, db: AsyncSession = Depends(get_db)):
    incident = await get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentResponse(
        id=incident.id,
        title=incident.title,
        status=incident.status.value if hasattr(incident.status, "value") else str(incident.status),
        severity=incident.severity.value if hasattr(incident.severity, "value") else str(incident.severity),
        violation_id=incident.violation_id,
        session_id=incident.session_id,
        policy_name=incident.policy_name,
        regulation=incident.regulation,
        regulation_article=incident.regulation_article,
        decision_chain_snapshot=incident.decision_chain_snapshot,
        affected_data_subjects=incident.affected_data_subjects,
        remediation_path=incident.remediation_path,
        resolution_notes=incident.resolution_notes,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
    )


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident_status(
    incident_id: str,
    body: IncidentUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    updates = body.model_dump(exclude_none=True)
    incident = await update_incident(db, incident_id, updates)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentResponse(
        id=incident.id,
        title=incident.title,
        status=incident.status.value if hasattr(incident.status, "value") else str(incident.status),
        severity=incident.severity.value if hasattr(incident.severity, "value") else str(incident.severity),
        violation_id=incident.violation_id,
        session_id=incident.session_id,
        policy_name=incident.policy_name,
        regulation=incident.regulation,
        regulation_article=incident.regulation_article,
        decision_chain_snapshot=incident.decision_chain_snapshot,
        affected_data_subjects=incident.affected_data_subjects,
        remediation_path=incident.remediation_path,
        resolution_notes=incident.resolution_notes,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
    )
