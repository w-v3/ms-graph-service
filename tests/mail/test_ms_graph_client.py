import pytest
from datetime import datetime, timedelta, timezone

import requests
from unittest.mock import MagicMock, patch

from app.mail.ms_graph_client import GraphMailClient
from app.schemas.email import EmailCreate


class DummyAuthFlow:
    """A fake auth flow that returns a constant token dict."""
    def __init__(self, token):
        self._token = token

    def acquire_token(self):
        return self._token


@pytest.fixture
def client(tmp_path):
    """Return a GraphMailClient with a dummy auth flow."""
    token = {"access_token": "fake-token"}
    auth = DummyAuthFlow(token)
    # Use a fake base URL so we don't accidentally hit real Graph
    api_url = "https://graph.microsoft.com/v1.0"
    c = GraphMailClient(auth, user_email="me@example.com", api_url=api_url)
    # Override requests.post/get so they don't use real network
    return c


# send_email tests

@patch.object(requests, "post")
@pytest.mark.asyncio
async def test_send_email_success(mock_post, client):
    mock_resp = MagicMock(status_code=202)
    mock_post.return_value = mock_resp

    email = EmailCreate(
        recipients=["a@x.com"],
        subject="Hi",
        body="Body",
        attachments=None,
    )
    result = await client.send_email(email)
    assert result is True
    mock_post.assert_called_once()
    url_called = mock_post.call_args[0][0]
    assert url_called.endswith("/sendMail")

@patch.object(requests, "post")
@pytest.mark.asyncio
async def test_send_email_failure_code(mock_post, client):
    mock_resp = MagicMock(status_code=400, text="Bad Request")
    mock_post.return_value = mock_resp

    email = EmailCreate(
        recipients=["a@x.com"],
        subject="Hi",
        body="Body",
    )
    result = await client.send_email(email)
    assert result is False

@patch.object(requests, "post", side_effect=Exception("Boom"))
@pytest.mark.asyncio
async def test_send_email_exception(mock_post, client):
    email = EmailCreate(
        recipients=["a@x.com"],
        subject="Hi",
        body="Body",
    )
    result = await client.send_email(email)
    assert result is False


# fetch_emails tests

@patch.object(requests, "get")
@pytest.mark.asyncio
async def test_fetch_emails_initial_and_update(mock_get, client):
    # First call: returns 2 messages
    now = datetime.now(timezone.utc)
    msg1 = {"receivedDateTime": (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")}
    msg2 = {"receivedDateTime": now.strftime("%Y-%m-%dT%H:%M:%SZ")}
    mock_get.return_value = MagicMock(status_code=200, json=lambda: {"value": [msg1, msg2]})

    # First fetch: should return both and set last_fetch_time to msg2 time
    messages = await client.fetch_emails()
    assert messages == [msg1, msg2]
    assert client.last_fetch_time.isoformat().startswith(now.isoformat()[:19])

    # Prepare second call: only returns msg2 onwards
    mock_get.reset_mock()
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {"value": [msg2]}
    )

    # Second fetch: using filter, returns only the new list
    messages2 = await client.fetch_emails()
    assert messages2 == [msg2]
    mock_get.assert_called_once()
    # Ensure the URL includes the filter with the previous timestamp
    called_url = mock_get.call_args[0][0]
    assert "$filter=receivedDateTime ge" in called_url

@patch.object(requests, "get")
@pytest.mark.asyncio
async def test_fetch_emails_non_200(mock_get, client):
    mock_get.return_value = MagicMock(status_code=500, text="Error")
    messages = await client.fetch_emails()
    assert messages == []

@patch.object(requests, "get", side_effect=Exception("Fail network"))
@pytest.mark.asyncio
async def test_fetch_emails_exception(mock_get, client):
    messages = await client.fetch_emails()
    assert messages == []
