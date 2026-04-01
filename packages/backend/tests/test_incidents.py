"""Tests for the incidents API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_incidents_empty(client: AsyncClient):
    response = await client.get("/api/v1/incidents")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["incidents"] == []


@pytest.mark.asyncio
async def test_list_incidents_with_status_filter(client: AsyncClient):
    response = await client.get("/api/v1/incidents?status=open")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_incidents_with_severity_filter(client: AsyncClient):
    response = await client.get("/api/v1/incidents?severity=critical")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_unknown_incident(client: AsyncClient):
    response = await client.get("/api/v1/incidents/nonexistent-id")
    assert response.status_code == 404
