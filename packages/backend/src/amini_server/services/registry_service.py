from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.agent import Agent
from ..models.session import AgentSession
from ..models.violation import PolicyViolation


async def list_agents(
    db: AsyncSession,
    framework: str | None = None,
    risk_class: str | None = None,
    deployment_status: str | None = None,
    discovery_method: str | None = None,
) -> tuple[list[dict], int]:
    query = select(Agent)

    if framework:
        query = query.where(Agent.framework == framework)
    if risk_class:
        query = query.where(Agent.risk_class == risk_class)
    if deployment_status:
        query = query.where(Agent.deployment_status == deployment_status)
    if discovery_method:
        query = query.where(Agent.discovery_method == discovery_method)

    query = query.order_by(Agent.created_at.desc())
    result = await db.execute(query)
    agents = list(result.scalars().all())

    entries = []
    for agent in agents:
        session_count = await db.execute(
            select(func.count()).select_from(AgentSession).where(
                AgentSession.agent_id == agent.id
            )
        )
        violation_count = await db.execute(
            select(func.count()).select_from(PolicyViolation)
            .join(AgentSession, PolicyViolation.session_id == AgentSession.id)
            .where(AgentSession.agent_id == agent.id)
        )
        entries.append({
            "id": agent.id,
            "agent_external_id": agent.agent_external_id,
            "name": agent.name,
            "description": agent.description,
            "framework": agent.framework,
            "provider": agent.provider,
            "risk_class": agent.risk_class,
            "tags": agent.tags,
            "data_access_patterns": agent.data_access_patterns,
            "deployment_status": agent.deployment_status,
            "discovery_method": agent.discovery_method,
            "regulations": agent.regulations,
            "session_count": session_count.scalar() or 0,
            "violation_count": violation_count.scalar() or 0,
            "created_at": agent.created_at,
            "updated_at": agent.updated_at,
        })

    return entries, len(entries)


async def get_agent_entry(db: AsyncSession, agent_id: str) -> dict | None:
    """Return a single agent dict with session/violation counts (same shape as list_agents entries)."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if agent is None:
        return None

    session_count = await db.execute(
        select(func.count()).select_from(AgentSession).where(
            AgentSession.agent_id == agent.id
        )
    )
    violation_count = await db.execute(
        select(func.count()).select_from(PolicyViolation)
        .join(AgentSession, PolicyViolation.session_id == AgentSession.id)
        .where(AgentSession.agent_id == agent.id)
    )
    return {
        "id": agent.id,
        "agent_external_id": agent.agent_external_id,
        "name": agent.name,
        "description": agent.description,
        "framework": agent.framework,
        "provider": agent.provider,
        "risk_class": agent.risk_class,
        "tags": agent.tags,
        "data_access_patterns": agent.data_access_patterns,
        "deployment_status": agent.deployment_status,
        "discovery_method": agent.discovery_method,
        "regulations": agent.regulations,
        "session_count": session_count.scalar() or 0,
        "violation_count": violation_count.scalar() or 0,
        "created_at": agent.created_at,
        "updated_at": agent.updated_at,
    }


async def get_agent(db: AsyncSession, agent_id: str) -> Agent | None:
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    return result.scalar_one_or_none()


async def update_agent(db: AsyncSession, agent_id: str, updates: dict) -> Agent | None:
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if agent is None:
        return None

    for key, value in updates.items():
        if value is not None and hasattr(agent, key):
            setattr(agent, key, value)

    await db.flush()
    await db.commit()
    return agent
