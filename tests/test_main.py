# tests/test_main.py
import pytest
import httpx
from fastapi import FastAPI

from app.main import app
from app.core.config import settings

from unittest.mock import AsyncMock, patch

from app.main import startup, shutdown

@pytest.mark.asyncio
async def test_root_endpoint():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Microsoft Graph API Email Service"}


def test_router_prefix_in_routes():
    """
    Ensure that at least one route includes the configured API prefix for emails.
    """
    prefix = f"{settings.API_V1_STR}/emails"
    all_paths = [route.path for route in app.routes]
    matched = any(path.startswith(prefix) for path in all_paths)
    assert matched, f"No route starts with prefix {prefix}"

def test_openapi_url():
     assert app.openapi_url == f"{settings.API_V1_STR}/openapi.json"


def test_project_metadata():
    assert app.title == settings.PROJECT_NAME


def test_middleware_applied():
    middleware_classes = [middleware.cls.__name__ for middleware in app.user_middleware]
    assert "CORSMiddleware" in middleware_classes


@pytest.mark.asyncio
async def test_startup_handler():
    with patch("app.main.mongo_mgr.ensure_database", new_callable=AsyncMock) as mock_ensure_db, \
         patch("app.main.scheduler.start") as mock_scheduler_start, \
         patch("app.main.scheduler.add_job") as mock_add_job:

        await startup()

        mock_ensure_db.assert_awaited_once()
        mock_add_job.assert_called_once()
        mock_scheduler_start.assert_called_once()


@pytest.mark.asyncio
async def test_shutdown_handler():
    with patch("app.main.mongo_mgr.close", new_callable=AsyncMock) as mock_close_db, \
         patch("app.main.scheduler.shutdown") as mock_scheduler_shutdown:

        await shutdown()

        mock_close_db.assert_awaited_once()
        mock_scheduler_shutdown.assert_called_once()