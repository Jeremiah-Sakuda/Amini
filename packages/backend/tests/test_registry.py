"""Tests for the agent registry API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_registry_empty(client: AsyncClient):
    response = await client.get("/api/v1/registry")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 0
    assert isinstance(data["agents"], list)


@pytest.mark.asyncio
async def test_get_unknown_agent(client: AsyncClient):
    response = await client.get("/api/v1/registry/nonexistent-agent")
    assert response.status_code == 404
