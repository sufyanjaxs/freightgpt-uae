import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture
async def auth_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/auth/register", json={
            "email": "api-test@freightgpt.ae",
            "password": "testpass123",
            "full_name": "API Test",
        })
        return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_load(auth_token):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/loads",
            json={
                "origin_city": "Dubai",
                "destination_city": "Abu Dhabi",
                "pickup_date": "2025-02-01T08:00:00Z",
                "weight_kg": 10000,
                "commodity": "General Freight",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["origin_city"] == "Dubai"
        assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_list_loads(auth_token):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/loads",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_dashboard_analytics(auth_token):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/analytics/dashboard",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "active_loads" in data
        assert "available_trucks" in data
