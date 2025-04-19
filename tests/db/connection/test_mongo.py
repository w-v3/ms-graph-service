import pytest
from pymongo.errors import PyMongoError
from unittest.mock import AsyncMock

import app.db.connection.mongo as mongo_module
from app.db.connection.mongo import MongoConnectionManager


class FakeDB:
    """Simulates a Motor DB with list_collection_names / create_collection."""
    def __init__(self):
        self.collections = []
        self.created = []

    async def list_collection_names(self):
        return self.collections

    async def create_collection(self, name):
        self.created.append(name)


class FakeClient:
    """Simulates AsyncIOMotorClient returning a single FakeDB on indexing."""
    def __init__(self, uri, fake_db: FakeDB):
        self.uri = uri
        self._db = fake_db
        self.closed = False

    def __getitem__(self, name):
        # Simulate client[name] → db
        return self._db

    def close(self):
        self.closed = True


@pytest.fixture
def fake_motor_client(monkeypatch):
    """
    Patch AsyncIOMotorClient so that any instantiation
    returns a single FakeClient wrapping a FakeDB.
    """
    fake_db = FakeDB()
    fake_client = FakeClient("dummy_uri", fake_db)

    def _fake_async_client(uri):
        assert uri == "mongodb://test:123@localhost"  # ensure correct URI passed
        return fake_client

    monkeypatch.setattr(
        mongo_module,
        "AsyncIOMotorClient",
        _fake_async_client,
    )
    return fake_client, fake_db


@pytest.mark.asyncio
async def test_connect_creates_client_and_returns_db(fake_motor_client):
    client, fake_db = fake_motor_client
    mgr = MongoConnectionManager("mongodb://test:123@localhost", "mydb")

    # First connect: should create the client
    db1 = await mgr.connect()
    assert db1 is fake_db
    # The manager.client should now be our fake_client
    assert mgr.client is client

    # Second connect: should reuse the same client, not re-instantiate
    db2 = await mgr.connect()
    assert db2 is fake_db
    # Confirm AsyncIOMotorClient was only called once (client is same object)
    assert mgr.client is client


@pytest.mark.asyncio
async def test_close_closes_client(fake_motor_client):
    client, _ = fake_motor_client
    mgr = MongoConnectionManager("mongodb://test:123@localhost", "mydb")
    # Manually assign the fake client so close() has something
    mgr.client = client

    await mgr.close()
    assert client.closed is True


@pytest.mark.asyncio
async def test_ensure_database_creates_collection_if_missing(fake_motor_client):
    _, fake_db = fake_motor_client
    fake_db.collections = []  # no collections exist yet
    mgr = MongoConnectionManager("mongodb://test:123@localhost", "newcoll")

    # Should create 'newcoll' since it's missing
    await mgr.ensure_database()
    assert fake_db.created == ["newcoll"]


@pytest.mark.asyncio
async def test_ensure_database_skips_if_exists(fake_motor_client):
    _, fake_db = fake_motor_client
    fake_db.collections = ["mycoll"]  # collection already exists
    fake_db.created.clear()

    mgr = MongoConnectionManager("mongodb://test:123@localhost", "mycoll")
    await mgr.ensure_database()
    # No new collections created
    assert fake_db.created == []


@pytest.mark.asyncio
async def test_ensure_database_raises_on_pymongo_error(monkeypatch):
    """
    Simulate a PyMongoError during list_collection_names
    to ensure it's logged and re-raised.
    """
    class BadDB:
        async def list_collection_names(self):
            raise PyMongoError("fail-list")

        async def create_collection(self, name):
            pass  # not reached

    # Override connect() to return our BadDB
    mgr = MongoConnectionManager("mongodb://test:123@localhost", "anycoll")
    mgr.connect = AsyncMock(return_value=BadDB())

    with pytest.raises(PyMongoError):
        await mgr.ensure_database()
