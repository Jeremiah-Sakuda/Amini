import pytest
from httpx import AsyncClient

from .factories import make_event, make_event_batch

AUTH_HEADER = {"Authorization": "Bearer dev-key"}


@pytest.mark.asyncio
async def test_ingest_single_event(client: AsyncClient):
    event = make_event()
    response = await client.post("/api/v1/events", json=event, headers=AUTH_HEADER)
    assert response.status_code == 202
    data = response.json()
    assert "event_id" in data


@pytest.mark.asyncio
async def test_ingest_event_batch(client: AsyncClient):
    events = make_event_batch()
    response = await client.post("/api/v1/events/batch", json={"events": events}, headers=AUTH_HEADER)
    assert response.status_code == 202
    data = response.json()
    assert data["accepted"] == 4


@pytest.mark.asyncio
async def test_ingest_empty_batch_fails(client: AsyncClient):
    response = await client.post("/api/v1/events/batch", json={"events": []}, headers=AUTH_HEADER)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ingest_without_auth_rejected(client: AsyncClient):
    event = make_event()
    response = await client.post("/api/v1/events", json=event)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_ingest_with_invalid_key_rejected(client: AsyncClient):
    event = make_event()
    response = await client.post(
        "/api/v1/events", json=event,
        headers={"Authorization": "Bearer wrong-key"},
    )
    assert response.status_code == 401
