# tests/test_endpoints.py

import pytest
import httpx
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.main import app
from app.dependencies import get_email_manager
from app.schemas.email import EmailCreate

from app.core.config import settings

# Build the full prefix from settings
EMAIL_PREFIX = f"{settings.API_V1_STR}/emails"



@pytest.fixture
def async_client():
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")

class MockEmailManager:
    async def send_email(self, email):
        return 200

    async def sync_and_store_emails(self):
        return ["msg1", "msg2"]


# Override the EmailManager dependency with a mock
@pytest.fixture(autouse=True)
def override_dependency():
    app.dependency_overrides[get_email_manager] = lambda: MockEmailManager()
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_check(async_client):
    url = f"{EMAIL_PREFIX}/health"
    async with async_client as client:
        response = await client.get(url)
    assert response.status_code == 200
    assert response.json() == {"status": "All good"}

@pytest.mark.asyncio
async def test_send_email_success(async_client):
    url = f"{EMAIL_PREFIX}/send"
    payload = {
        "subject": "Hello!",
        "body": "This is a test.",
        "recipients": ["someone@example.com"]
    }
    async with async_client as client:
        response = await client.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status_code"] == 200
    assert 'subject' in data["email"] and data['email']['subject'] == payload['subject']
    assert 'body' in data["email"] and data['email']['body'] == payload['body']
    assert 'recipients' in data["email"] and data['email']['recipients'] == payload['recipients']

@pytest.mark.asyncio
async def test_fetch_emails(async_client):
    url = f"{EMAIL_PREFIX}/fetch"
    async with async_client as client:
        response = await client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["status_code"] == 200
    assert data["count"] == 2