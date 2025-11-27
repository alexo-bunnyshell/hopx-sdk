"""Tests for API key management.

Tests cover:
- APIKeyManager initialization
- List, create, revoke, and get key operations
- Error handling for API failures
- Context manager support
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestAPIKeyManagerInit:
    """Tests for APIKeyManager initialization."""

    @pytest.mark.unit
    def test_init_with_defaults(self) -> None:
        """Initializes with default base URL."""
        from hopx_cli.auth.api_keys import APIKeyManager

        with patch("hopx_cli.auth.api_keys.httpx.Client") as mock_client:
            _manager = APIKeyManager("test_token")

            mock_client.assert_called_once()
            call_kwargs = mock_client.call_args.kwargs
            assert call_kwargs["base_url"] == "https://api.hopx.dev"
            assert "Bearer test_token" in call_kwargs["headers"]["Authorization"]

    @pytest.mark.unit
    def test_init_with_custom_base_url(self) -> None:
        """Initializes with custom base URL."""
        from hopx_cli.auth.api_keys import APIKeyManager

        with patch("hopx_cli.auth.api_keys.httpx.Client") as mock_client:
            _manager = APIKeyManager("test_token", base_url="https://custom.api.com")

            call_kwargs = mock_client.call_args.kwargs
            assert call_kwargs["base_url"] == "https://custom.api.com"

    @pytest.mark.unit
    def test_context_manager_entry(self) -> None:
        """Context manager returns self on entry."""
        from hopx_cli.auth.api_keys import APIKeyManager

        with patch("hopx_cli.auth.api_keys.httpx.Client"):
            manager = APIKeyManager("test_token")
            with manager as ctx:
                assert ctx is manager

    @pytest.mark.unit
    def test_context_manager_exit_closes_client(self) -> None:
        """Context manager closes client on exit."""
        from hopx_cli.auth.api_keys import APIKeyManager

        mock_client = MagicMock()
        with patch("hopx_cli.auth.api_keys.httpx.Client", return_value=mock_client):
            manager = APIKeyManager("test_token")
            with manager:
                pass
            mock_client.close.assert_called_once()

    @pytest.mark.unit
    def test_close_closes_client(self) -> None:
        """Close method closes HTTP client."""
        from hopx_cli.auth.api_keys import APIKeyManager

        mock_client = MagicMock()
        with patch("hopx_cli.auth.api_keys.httpx.Client", return_value=mock_client):
            manager = APIKeyManager("test_token")
            manager.close()
            mock_client.close.assert_called_once()


class TestAPIKeyManagerListKeys:
    """Tests for APIKeyManager.list_keys()."""

    @pytest.mark.unit
    def test_list_keys_success(self) -> None:
        """Returns list of keys on success."""
        from hopx_cli.auth.api_keys import APIKeyManager

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "api_keys": [
                {"id": "key1", "name": "test-key", "status": "active"},
                {"id": "key2", "name": "another-key", "status": "active"},
            ],
            "count": 2,
        }

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response

        with patch("hopx_cli.auth.api_keys.httpx.Client", return_value=mock_client):
            manager = APIKeyManager("test_token")
            keys = manager.list_keys()

            assert len(keys) == 2
            assert keys[0]["id"] == "key1"
            mock_client.get.assert_called_once_with("/auth/api-keys")

    @pytest.mark.unit
    def test_list_keys_empty(self) -> None:
        """Returns empty list when no keys exist."""
        from hopx_cli.auth.api_keys import APIKeyManager

        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "api_keys": [], "count": 0}

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response

        with patch("hopx_cli.auth.api_keys.httpx.Client", return_value=mock_client):
            manager = APIKeyManager("test_token")
            keys = manager.list_keys()
            assert keys == []

    @pytest.mark.unit
    def test_list_keys_raises_on_failure(self) -> None:
        """Raises RuntimeError when API returns success=false."""
        from hopx_cli.auth.api_keys import APIKeyManager

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": False,
            "message": "Unauthorized",
        }

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response

        with patch("hopx_cli.auth.api_keys.httpx.Client", return_value=mock_client):
            manager = APIKeyManager("test_token")
            with pytest.raises(RuntimeError, match="Unauthorized"):
                manager.list_keys()


class TestAPIKeyManagerCreateKey:
    """Tests for APIKeyManager.create_key()."""

    @pytest.mark.unit
    def test_create_key_success(self) -> None:
        """Creates key and returns full key value."""
        from hopx_cli.auth.api_keys import APIKeyManager

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "message": "API key created successfully",
            "api_key": {"id": "key1", "name": "my-key", "status": "active"},
            "full_key": "hopx_live_xxx.secret",
        }

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response

        with patch("hopx_cli.auth.api_keys.httpx.Client", return_value=mock_client):
            manager = APIKeyManager("test_token")
            result = manager.create_key("my-key", expires_in="never")

            assert result["full_key"] == "hopx_live_xxx.secret"
            assert result["api_key"]["name"] == "my-key"
            mock_client.post.assert_called_once_with(
                "/auth/api-keys",
                json={"name": "my-key", "expires_in": "never"},
            )

    @pytest.mark.unit
    def test_create_key_with_expiry(self) -> None:
        """Creates key with expiration."""
        from hopx_cli.auth.api_keys import APIKeyManager

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "api_key": {"id": "key1"},
            "full_key": "hopx_live_xxx.secret",
        }

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response

        with patch("hopx_cli.auth.api_keys.httpx.Client", return_value=mock_client):
            manager = APIKeyManager("test_token")
            manager.create_key("test-key", expires_in="3months")

            call_kwargs = mock_client.post.call_args.kwargs
            assert call_kwargs["json"]["expires_in"] == "3months"

    @pytest.mark.unit
    def test_create_key_invalid_expiry(self) -> None:
        """Raises ValueError for invalid expiration."""
        from hopx_cli.auth.api_keys import APIKeyManager

        with patch("hopx_cli.auth.api_keys.httpx.Client"):
            manager = APIKeyManager("test_token")
            with pytest.raises(ValueError, match="Invalid expires_in"):
                manager.create_key("test-key", expires_in="invalid")  # type: ignore

    @pytest.mark.unit
    def test_create_key_raises_on_failure(self) -> None:
        """Raises RuntimeError when API returns success=false."""
        from hopx_cli.auth.api_keys import APIKeyManager

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": False,
            "message": "Rate limit exceeded",
        }

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response

        with patch("hopx_cli.auth.api_keys.httpx.Client", return_value=mock_client):
            manager = APIKeyManager("test_token")
            with pytest.raises(RuntimeError, match="Rate limit exceeded"):
                manager.create_key("test-key")

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "expires_in",
        ["1month", "3months", "6months", "1year", "never"],
    )
    def test_create_key_valid_expiry_options(self, expires_in: str) -> None:
        """Accepts all valid expiration options."""
        from hopx_cli.auth.api_keys import APIKeyManager

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "api_key": {},
            "full_key": "test",
        }

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response

        with patch("hopx_cli.auth.api_keys.httpx.Client", return_value=mock_client):
            manager = APIKeyManager("test_token")
            manager.create_key("test-key", expires_in=expires_in)  # type: ignore


class TestAPIKeyManagerRevokeKey:
    """Tests for APIKeyManager.revoke_key()."""

    @pytest.mark.unit
    def test_revoke_key_success(self) -> None:
        """Returns True on successful revocation."""
        from hopx_cli.auth.api_keys import APIKeyManager

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "message": "API key revoked successfully",
        }

        mock_client = MagicMock()
        mock_client.delete.return_value = mock_response

        with patch("hopx_cli.auth.api_keys.httpx.Client", return_value=mock_client):
            manager = APIKeyManager("test_token")
            result = manager.revoke_key("key123")

            assert result is True
            mock_client.delete.assert_called_once_with("/auth/api-keys/key123")

    @pytest.mark.unit
    def test_revoke_key_returns_false_on_failure(self) -> None:
        """Returns False when API returns success=false."""
        from hopx_cli.auth.api_keys import APIKeyManager

        mock_response = MagicMock()
        mock_response.json.return_value = {"success": False}

        mock_client = MagicMock()
        mock_client.delete.return_value = mock_response

        with patch("hopx_cli.auth.api_keys.httpx.Client", return_value=mock_client):
            manager = APIKeyManager("test_token")
            result = manager.revoke_key("key123")
            assert result is False


class TestAPIKeyManagerGetKey:
    """Tests for APIKeyManager.get_key()."""

    @pytest.mark.unit
    def test_get_key_success(self) -> None:
        """Returns key details on success."""
        from hopx_cli.auth.api_keys import APIKeyManager

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "api_key": {
                "id": "key123",
                "name": "my-key",
                "status": "active",
                "masked_key": "hopx_live_xxx...***",
            },
        }

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response

        with patch("hopx_cli.auth.api_keys.httpx.Client", return_value=mock_client):
            manager = APIKeyManager("test_token")
            key = manager.get_key("key123")

            assert key["id"] == "key123"
            assert key["name"] == "my-key"
            mock_client.get.assert_called_once_with("/auth/api-keys/key123")

    @pytest.mark.unit
    def test_get_key_raises_on_failure(self) -> None:
        """Raises RuntimeError when API returns success=false."""
        from hopx_cli.auth.api_keys import APIKeyManager

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": False,
            "message": "Key not found",
        }

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response

        with patch("hopx_cli.auth.api_keys.httpx.Client", return_value=mock_client):
            manager = APIKeyManager("test_token")
            with pytest.raises(RuntimeError, match="Key not found"):
                manager.get_key("nonexistent")


class TestExpiresOptions:
    """Tests for EXPIRES_OPTIONS constant."""

    @pytest.mark.unit
    def test_expires_options_contains_expected_values(self) -> None:
        """EXPIRES_OPTIONS contains all valid values."""
        from hopx_cli.auth.api_keys import EXPIRES_OPTIONS

        assert "1month" in EXPIRES_OPTIONS
        assert "3months" in EXPIRES_OPTIONS
        assert "6months" in EXPIRES_OPTIONS
        assert "1year" in EXPIRES_OPTIONS
        assert "never" in EXPIRES_OPTIONS
        assert len(EXPIRES_OPTIONS) == 5
