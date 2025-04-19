# tests/test_dependencies.py

import pytest
from unittest.mock import AsyncMock, patch
from app.dependencies import (
    get_mail_client,
    get_email_repo,
    get_email_manager,
    run_email_sync,
)
from app.mail.ms_graph_client import GraphMailClient
from app.db.mongo_email_repository import MongoEmailRepository
from app.services.email_manager import EmailManager


def test_get_mail_client_returns_graph_mail_client():
    client = get_mail_client()
    assert isinstance(client, GraphMailClient)


def test_get_email_repo_returns_mongo_email_repository():
    repo = get_email_repo()
    assert isinstance(repo, MongoEmailRepository)


def test_get_email_manager_returns_email_manager():
    manager = get_email_manager()
    assert isinstance(manager, EmailManager)


def test_lru_cache_returns_same_instances():
    assert get_mail_client() is get_mail_client()
    assert get_email_repo() is get_email_repo()
    assert get_email_manager() is get_email_manager()

@pytest.mark.asyncio
@patch("app.dependencies.get_email_manager")
async def test_run_email_sync_success(mock_get_manager):
    mock_manager = AsyncMock()
    mock_get_manager.return_value = mock_manager

    await run_email_sync()

    mock_manager.sync_and_store_emails.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.dependencies.get_email_manager")
async def test_run_email_sync_handles_exception(mock_get_manager, capsys):
    mock_manager = AsyncMock()
    mock_manager.sync_and_store_emails.side_effect = Exception("Some sync error")
    mock_get_manager.return_value = mock_manager

    await run_email_sync()

    captured = capsys.readouterr()
    assert "CRON JOB ERROR: Some sync error" in captured.out