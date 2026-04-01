"""Tests for the audit reports API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_reports_empty(client: AsyncClient):
    response = await client.get("/api/v1/reports")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["reports"] == []


@pytest.mark.asyncio
async def test_generate_report(client: AsyncClient):
    response = await client.post("/api/v1/reports", json={
        "framework": "eu-ai-act",
        "period_start": "2026-01-01",
        "period_end": "2026-03-31",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["framework"] == "eu-ai-act"
    assert data["status"] == "completed"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_report_detail(client: AsyncClient):
    # Create a report first
    create_resp = await client.post("/api/v1/reports", json={
        "framework": "soc2",
        "period_start": "2026-01-01",
        "period_end": "2026-03-31",
    })
    report_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/reports/{report_id}")
    assert response.status_code == 200
    assert response.json()["id"] == report_id


@pytest.mark.asyncio
async def test_get_unknown_report(client: AsyncClient):
    response = await client.get("/api/v1/reports/nonexistent-id")
    assert response.status_code == 404
