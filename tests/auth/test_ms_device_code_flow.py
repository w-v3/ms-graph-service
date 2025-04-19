import os
import pytest
from unittest.mock import patch, MagicMock
from app.auth.ms_device_code_flow import DeviceCodeFlow

@pytest.fixture
def tmp_cache_file(tmp_path, monkeypatch):
    # Ensure no real cache is loaded or written
    cache = tmp_path / "token_cache.json"
    monkeypatch.chdir(tmp_path)           # cwd so relative paths work
    return str(cache)

@patch("app.auth.ms_device_code_flow.msal.PublicClientApplication")
def test_acquire_token_silent_success(mock_pca, tmp_cache_file):
    # Arrange: PCA returns one account and a valid silent token
    mock_app = MagicMock()
    mock_app.get_accounts.return_value = ["acct1"]
    mock_app.acquire_token_silent.return_value = {"access_token": "silent-token"}
    mock_pca.return_value = mock_app

    flow = DeviceCodeFlow(
        client_id="cid",
        tenant="tid",
        scopes=["s1"],
        auth_url="https://login",
        cache_file=tmp_cache_file
    )

    # Act
    result = flow.acquire_token()

    # Assert
    assert result == {"access_token": "silent-token"}
    mock_app.acquire_token_silent.assert_called_once_with(["s1"], account="acct1")

@patch("app.auth.ms_device_code_flow.msal.PublicClientApplication")
def test_acquire_token_device_flow_success(mock_pca, tmp_cache_file):
    # Arrange: no accounts, device flow returns user_code, then returns a token
    mock_app = MagicMock()
    mock_app.get_accounts.return_value = []
    device_flow_response = {"user_code": "ABC123", "message": "Use this code"}
    mock_app.initiate_device_flow.return_value = device_flow_response
    mock_app.acquire_token_by_device_flow.return_value = {"access_token": "device-token"}
    mock_pca.return_value = mock_app

    flow = DeviceCodeFlow(
        client_id="cid",
        tenant="tid",
        scopes=["s1"],
        auth_url="https://login",
        cache_file=tmp_cache_file
    )

    # Act
    result = flow.acquire_token()

    # Assert
    assert result == {"access_token": "device-token"}
    mock_app.initiate_device_flow.assert_called_once_with(scopes=["s1"])
    mock_app.acquire_token_by_device_flow.assert_called_once_with(device_flow_response)

@patch("app.auth.ms_device_code_flow.msal.PublicClientApplication")
def test_acquire_token_device_flow_init_failure(mock_pca, tmp_cache_file):
    # Arrange: no accounts, device flow returns error (no user_code)
    mock_app = MagicMock()
    mock_app.get_accounts.return_value = []
    mock_app.initiate_device_flow.return_value = {
        "error": "invalid_request",
        "error_description": "Bad scope"
    }
    mock_pca.return_value = mock_app

    flow = DeviceCodeFlow(
        client_id="cid",
        tenant="tid",
        scopes=["s1"],
        auth_url="https://login",
        cache_file=tmp_cache_file
    )

    # Act & Assert
    with pytest.raises(Exception) as excinfo:
        flow.acquire_token()

    assert "Device‑flow init failed: invalid_request — Bad scope" in str(excinfo.value)
