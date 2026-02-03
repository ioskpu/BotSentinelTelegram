import pytest
import pytest_asyncio
from httpx import AsyncClient
from src.api.main import app
from src.api.middleware.auth import create_access_token
from src.database.mongodb import mongodb
from datetime import timedelta

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    # Setup test database
    # In a real scenario, we would use a test database URI
    yield
    # Cleanup if necessary

@pytest_asyncio.fixture
async def test_user():
    user_data = {
        "telegram_id": 123456,
        "first_name": "Test",
        "username": "testuser"
    }
    await mongodb.users.update_one(
        {"telegram_id": 123456},
        {"$set": user_data},
        upsert=True
    )
    # Create an active session
    await mongodb.sessions.update_one(
        {"user_telegram_id": 123456},
        {"$set": {"is_active": True}},
        upsert=True
    )
    return user_data

@pytest_asyncio.fixture
async def auth_token(test_user):
    return create_access_token({"telegram_id": test_user["telegram_id"]})

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_unauthorized_access():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/dashboard/metrics/market/overview")
    assert response.status_code == 403 # HTTPBearer auto_error

@pytest.mark.asyncio
async def test_authorized_access(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/dashboard/metrics/market/overview", headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_invalid_token():
    headers = {"Authorization": "Bearer invalid-token"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/dashboard/metrics/market/overview", headers=headers)
    assert response.status_code == 401
