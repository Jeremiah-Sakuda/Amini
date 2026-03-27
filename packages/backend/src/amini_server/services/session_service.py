from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.agent import Agent
from ..models.decision import DecisionNode
from ..models.session import AgentSession, SessionStatus
from ..models.violation import PolicyViolation


async def get_or_create_agent(db: AsyncSession, agent_external_id: str) -> Agent:
    result = await db.execute(
        select(Agent).where(Agent.agent_external_id == agent_external_id)
    )
    agent = result.scalar_one_or_none()
    if agent is None:
        agent = Agent(agent_external_id=agent_external_id, name=agent_external_id)
        db.add(agent)
        await db.flush()
    return agent


async def get_or_create_session(
    db: AsyncSession,
    agent_external_id: str,
    session_external_id: str,
    environment: str = "development",
    user_context: dict | None = None,
) -> AgentSession:
    result = await db.execute(
        select(AgentSession).where(
            AgentSession.session_external_id == session_external_id
        )
    )
    session = result.scalar_one_or_none()
    if session is None:
        agent = await get_or_create_agent(db, agent_external_id)
        session = AgentSession(
            agent_id=agent.id,
            session_external_id=session_external_id,
            environment=environment,
            user_context=user_context,
        )
        db.add(session)
        await db.flush()
    return session


async def list_sessions(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    agent_id: str | None = None,
    environment: str | None = None,
    status: str | None = None,
) -> tuple[list[AgentSession], int]:
    query = select(AgentSession).options(
        selectinload(AgentSession.decisions),
        selectinload(AgentSession.violations),
    )
    count_query = select(func.count()).select_from(AgentSession)

    if agent_id:
        agent_result = await db.execute(
            select(Agent).where(Agent.agent_external_id == agent_id)
        )
        agent = agent_result.scalar_one_or_none()
        if agent:
            query = query.where(AgentSession.agent_id == agent.id)
            count_query = count_query.where(AgentSession.agent_id == agent.id)
        else:
            return [], 0

    if environment:
        query = query.where(AgentSession.environment == environment)
        count_query = count_query.where(AgentSession.environment == environment)

    if status:
        query = query.where(AgentSession.status == SessionStatus(status))
        count_query = count_query.where(AgentSession.status == SessionStatus(status))

    query = query.order_by(AgentSession.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    sessions = list(result.scalars().unique().all())

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    return sessions, total


async def get_session_detail(db: AsyncSession, session_id: str) -> AgentSession | None:
    result = await db.execute(
        select(AgentSession)
        .options(
            selectinload(AgentSession.decisions),
            selectinload(AgentSession.violations),
        )
        .where(AgentSession.id == session_id)
    )
    return result.scalar_one_or_none()


async def close_session(
    db: AsyncSession, session_id: str, status: str = "completed", reason: str | None = None
) -> AgentSession | None:
    result = await db.execute(
        select(AgentSession).where(AgentSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if session:
        session.status = SessionStatus(status)
        session.terminal_reason = reason
        await db.flush()
    return session
