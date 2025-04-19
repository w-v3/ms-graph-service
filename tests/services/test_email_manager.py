import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.email_manager import EmailManager
from app.schemas.email import EmailCreate, EmailInDB
from datetime import datetime, timezone


@pytest.fixture
def email_create():
    return EmailCreate(
        id="email-id",
        subject="Test Subject",
        body="Hello World",
        recipients=["test@example.com"],
    )


@pytest.fixture
def valid_email_dict():
    # Minimal valid EmailInDB data
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "id": "email-123",
        "changeKey": "key-123",
        "createdDateTime": now,
        "lastModifiedDateTime": now,
        "receivedDateTime": now,
        "sentDateTime": now,
        "subject": "Hello",
        "bodyPreview": "Body preview",
        "body": {"content": "Full content", "contentType": "HTML"},
        "sender": {"emailAddress": {"name": "Alice", "address": "alice@example.com"}},
        "from": {"emailAddress": {"name": "Alice", "address": "alice@example.com"}},
        "toRecipients": [{"emailAddress": {"name": "Bob", "address": "bob@example.com"}}],
        "ccRecipients": [],
        "bccRecipients": [],
        "replyTo": [],
        "hasAttachments": False,
        "internetMessageId": "msgid",
        "importance": "normal",
        "parentFolderId": "pfid",
        "conversationId": "cid",
        "conversationIndex": "cidx",
        "isDeliveryReceiptRequested": False,
        "isReadReceiptRequested": False,
        "isRead": True,
        "isDraft": False,
        "webLink": None,
        "inferenceClassification": None,
        "flag": {"flagStatus": "notFlagged"},
        "categories": [],
    }


@pytest.mark.asyncio
async def test_send_email_success(email_create):
    mail_client = MagicMock()
    mail_client.send_email = AsyncMock(return_value=True)

    repo = MagicMock()

    manager = EmailManager(mail_client, repo)

    success = await manager.send_email(email_create)

    assert success is True
    mail_client.send_email.assert_awaited_once_with(email_create)


@pytest.mark.asyncio
async def test_send_email_failure(email_create):
    mail_client = MagicMock()
    mail_client.send_email = AsyncMock(return_value=False)

    repo = MagicMock()

    manager = EmailManager(mail_client, repo)

    success = await manager.send_email(email_create)

    assert success is False
    mail_client.send_email.assert_awaited_once_with(email_create)


@pytest.mark.asyncio
async def test_sync_and_store_emails(valid_email_dict):
    mail_client = MagicMock()
    mail_client.fetch_emails = AsyncMock(return_value=[valid_email_dict])

    repo = MagicMock()
    repo.upsert_email = AsyncMock()

    manager = EmailManager(mail_client, repo)

    result = await manager.sync_and_store_emails()

    assert len(result) == 1
    assert isinstance(result[0], EmailInDB)
    repo.upsert_email.assert_awaited_once()
    mail_client.fetch_emails.assert_awaited_once()


@pytest.mark.asyncio
async def test_sync_skips_invalid_emails(valid_email_dict):
    mail_client = MagicMock()
    mail_client.fetch_emails = AsyncMock(return_value=[valid_email_dict, {"invalid": "data"}])

    repo = MagicMock()
    repo.upsert_email = AsyncMock()

    manager = EmailManager(mail_client, repo)

    result = await manager.sync_and_store_emails()

    # Only one valid email should be stored
    assert len(result) == 1
    repo.upsert_email.assert_awaited_once()
    mail_client.fetch_emails.assert_awaited_once()
