# tests/test_mongo_email_repository.py

import pytest
import datetime as std_datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.db.mongo_email_repository import MongoEmailRepository
from app.schemas.email import EmailInDB, EmailCreate


class DummyEmailInDB:
    def __init__(self, id_, payload):
        self.id = id_
        self._payload = payload

    def model_dump(self, by_alias=False):
        return self._payload


class DummyEmailCreate:
    def __init__(self, id_, subject, body, recipients):
        self.id = id_
        self.subject = subject
        self.body = body
        self.recipients = recipients


@pytest.fixture
def fake_db_upsert():
    fake_col = MagicMock()
    fake_col.update_one = AsyncMock()
    fake_col.distinct = AsyncMock(return_value=["abc"])
    fake_cursor = MagicMock()
    fake_cursor.to_list = AsyncMock(return_value=[{"_id": "abc"}])
    fake_col.find.return_value = fake_cursor

    fake_db = MagicMock()
    fake_db.emails = fake_col

    class DummyManager:
        async def connect(self):
            return fake_db

    return fake_db, fake_col, DummyManager()


@pytest.mark.asyncio
async def test_upsert_email_calls_mongo_methods(fake_db_upsert):
    fake_db, fake_col, manager = fake_db_upsert
    repo = MongoEmailRepository(manager)

    payload = {"_id": "abc", "foo": "bar"}
    email = DummyEmailInDB("abc", payload)

    await repo.upsert_email(email)

    fake_col.update_one.assert_awaited_once_with(
        {"_id": "abc"}, {"$set": payload}, upsert=True
    )
    fake_col.distinct.assert_awaited_once_with("_id")
    fake_col.find.assert_called_once_with({"_id": "abc"})
    fake_col.find.return_value.to_list.assert_awaited_once_with(None)


@pytest.fixture
def fake_db_list():
    """
    Return a fake DB where
      db.emails.find().sort().limit() yields one complete doc
      that satisfies EmailInDB validation.
    """
    now = std_datetime.datetime.utcnow().replace(microsecond=0, tzinfo=std_datetime.timezone.utc)
    # Construct a fully valid document with all required fields:
    doc = {
        "_id": "id1",
        "changeKey": "ck1",
        "createdDateTime": now.isoformat().replace("+00:00", "Z"),
        "lastModifiedDateTime": now.isoformat().replace("+00:00", "Z"),
        "receivedDateTime": now.isoformat().replace("+00:00", "Z"),
        "sentDateTime": now.isoformat().replace("+00:00", "Z"),
        "subject": "Test",
        "bodyPreview": "Preview",
        "body": {"contentType": "HTML", "content": "Hello"},
        "sender": {"emailAddress": {"name": "Me", "address": "me@example.com"}},
        "from": {"emailAddress": {"name": "Me", "address": "me@example.com"}},
        "toRecipients": [{"emailAddress": {"name": "You", "address": "you@example.com"}}],
        "ccRecipients": [],
        "bccRecipients": [],
        "replyTo": [],
        "hasAttachments": False,
        "internetMessageId": None,
        "importance": "normal",
        "parentFolderId": None,
        "conversationId": "cid1",
        "conversationIndex": "cidx1",
        "isDeliveryReceiptRequested": False,
        "isReadReceiptRequested": False,
        "isRead": True,
        "isDraft": False,
        "webLink": None,
        "inferenceClassification": None,
        "flag": {"flagStatus": "notFlagged"},
        # categories is optional or may default; if required add it:
        "categories": []
    }

    class FakeCursor:
        def sort(self, *a, **k):
            return self
        def limit(self, *a, **k):
            return self
        async def __aiter__(self):
            yield doc

    fake_col = MagicMock()
    fake_col.find.return_value = FakeCursor()

    fake_db = MagicMock()
    fake_db.emails = fake_col

    class DummyManager:
        async def connect(self):
            return fake_db

    return fake_db, fake_col, DummyManager()


@pytest.mark.asyncio
async def test_list_recent_emails_returns_email_models(fake_db_list):
    _, fake_col, manager = fake_db_list
    repo = MongoEmailRepository(manager)

    results = await repo.list_recent_emails(limit=1)
    # Should yield exactly one EmailInDB instance
    assert isinstance(results, list) and len(results) == 1
    email = results[0]
    assert isinstance(email, EmailInDB)
    assert email.id == "id1"
    # Check a few other fields round‑trip correctly
    assert email.subject == "Test"
    assert email.body.content == "Hello"


@pytest.fixture
def fake_db_insert():
    fake_col = MagicMock()
    fake_col.insert_one = AsyncMock()

    fake_db = MagicMock()
    fake_db.emails = fake_col

    class DummyManager:
        async def connect(self):
            return fake_db

    return fake_db, fake_col, DummyManager()


@pytest.mark.asyncio
async def test_save_sent_email_calls_insert(fake_db_insert, monkeypatch):
    fake_db, fake_col, manager = fake_db_insert
    repo = MongoEmailRepository(manager)

    # Monkey-patch module datetime for consistent output
    import app.db.mongo_email_repository as repo_mod
    monkeypatch.setattr(repo_mod, "datetime", std_datetime.datetime)

    email = DummyEmailCreate(
        id_="eid",
        subject="Subj",
        body="Content",
        recipients=[{"address": "to@example.com"}]
    )

    await repo.save_sent_email(email)

    fake_col.insert_one.assert_awaited_once()
    args, _ = fake_col.insert_one.call_args
    doc = args[0]
    assert doc["_id"] == "eid"
    assert doc["subject"] == "Subj"
    assert doc["body"]["content"] == "Content"
    assert doc["status"] == "Sent"
    # sentDateTime now a real datetime
    assert isinstance(doc["sentDateTime"], std_datetime.datetime)
