from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db, verify_api_key
from ..schemas.registry import AgentRegistryEntry, AgentRegistryListResponse, AgentRegistryUpdate
from ..services.registry_service import get_agent, get_agent_entry, list_agents, update_agent

router = APIRouter(
    prefix="/api/v1/registry",
    tags=["agent-registry"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("", response_model=AgentRegistryListResponse)
async def get_agent_registry(
    framework: str | None = None,
    risk_class: str | None = None,
    deployment_status: str | None = None,
    discovery_method: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    entries, total = await list_agents(
        db,
        framework=framework,
        risk_class=risk_class,
        deployment_status=deployment_status,
        discovery_method=discovery_method,
    )
    return AgentRegistryListResponse(
        agents=[AgentRegistryEntry(**e) for e in entries],
        total=total,
    )


@router.get("/{agent_id}", response_model=AgentRegistryEntry)
async def get_agent_detail(agent_id: str, db: AsyncSession = Depends(get_db)):
    entry = await get_agent_entry(db, agent_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentRegistryEntry(**entry)


@router.patch("/{agent_id}", response_model=AgentRegistryEntry)
async def update_agent_registry(
    agent_id: str,
    body: AgentRegistryUpdate,
    db: AsyncSession = Depends(get_db),
):
    updates = body.model_dump(exclude_none=True)
    agent = await update_agent(db, agent_id, updates)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    entry = await get_agent_entry(db, agent_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentRegistryEntry(**entry)
