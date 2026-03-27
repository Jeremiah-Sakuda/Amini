import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from amini_server.services.session_service import get_or_create_session


@pytest.mark.asyncio
async def test_list_sessions_empty(client: AsyncClient):
    response = await client.get("/api/v1/sessions")
    assert response.status_code == 200
    data = response.json()
    assert data["sessions"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_sessions_with_data(client: AsyncClient, db: AsyncSession):
    await get_or_create_session(db, "agent-1", "sess-1", "test")
    await db.commit()

    response = await client.get("/api/v1/sessions")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["sessions"][0]["session_external_id"] == "sess-1"


@pytest.mark.asyncio
async def test_get_session_not_found(client: AsyncClient):
    response = await client.get("/api/v1/sessions/nonexistent")
    assert response.status_code == 404
