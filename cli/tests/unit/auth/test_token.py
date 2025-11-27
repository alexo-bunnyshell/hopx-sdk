"""Tests for token management.

Tests cover:
- API key retrieval from env and credential store
- OAuth token retrieval and refresh
- Authentication status checks
- Preferred token selection
"""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from hopx_cli.auth.token import TokenManager


class TestTokenManagerGetValidApiKey:
    """Tests for TokenManager.get_valid_api_key()."""

    @pytest.mark.unit
    def test_returns_env_api_key_first(
        self, temp_hopx_dir: Any, mock_keyring: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Environment variable takes priority over credential store."""
        from hopx_cli.auth.credentials import CredentialStore

        monkeypatch.setenv("HOPX_API_KEY", "env_api_key")
        store = CredentialStore()
        manager = TokenManager(store)

        result = manager.get_valid_api_key()
        assert result == "env_api_key"

    @pytest.mark.unit
    def test_returns_stored_key_when_no_env(
        self, temp_hopx_dir: Any, mock_keyring_with_api_key: MagicMock
    ) -> None:
        """Falls back to credential store when no env var."""
        from hopx_cli.auth.credentials import CredentialStore

        store = CredentialStore()
        manager = TokenManager(store)

        result = manager.get_valid_api_key()
        assert result == "hopx_live_stored.secret"

    @pytest.mark.unit
    def test_returns_none_when_no_key_found(
        self, temp_hopx_dir: Any, mock_keyring: MagicMock
    ) -> None:
        """Returns None when no API key in env or store."""
        from hopx_cli.auth.credentials import CredentialStore

        store = CredentialStore()
        manager = TokenManager(store)

        result = manager.get_valid_api_key()
        assert result is None


class TestTokenManagerGetValidOAuthToken:
    """Tests for TokenManager.get_valid_oauth_token()."""

    @pytest.mark.unit
    def test_returns_none_when_no_token(self, temp_hopx_dir: Any, mock_keyring: MagicMock) -> None:
        """Returns None when no OAuth token stored."""
        from hopx_cli.auth.credentials import CredentialStore

        store = CredentialStore()
        manager = TokenManager(store)

        result = manager.get_valid_oauth_token()
        assert result is None

    @pytest.mark.unit
    def test_returns_valid_token(self, temp_hopx_dir: Any) -> None:
        """Returns access token when valid and not expired."""
        from hopx_cli.auth.credentials import CredentialStore

        with patch("hopx_cli.auth.credentials.keyring") as mock:
            future_time = int(time.time()) + 3600  # 1 hour from now
            mock.get_password.side_effect = lambda _service, key: {
                "default:oauth_access": "valid_access_token",
                "default:oauth_refresh": "refresh_token",
                "default:oauth_expires": str(future_time),
            }.get(key)

            store = CredentialStore()
            manager = TokenManager(store)

            result = manager.get_valid_oauth_token()
            assert result == "valid_access_token"

    @pytest.mark.unit
    def test_refreshes_expiring_token(self, temp_hopx_dir: Any) -> None:
        """Refreshes token when within 5 minutes of expiry."""
        from hopx_cli.auth.credentials import CredentialStore

        with patch("hopx_cli.auth.credentials.keyring") as mock_keyring:
            # Token expires in 2 minutes (within 5 min window)
            expires_at = int(time.time()) + 120
            mock_keyring.get_password.side_effect = lambda _service, key: {
                "default:oauth_access": "old_access_token",
                "default:oauth_refresh": "refresh_token",
                "default:oauth_expires": str(expires_at),
            }.get(key)

            with patch("hopx_cli.auth.token.refresh_oauth_token") as mock_refresh:
                mock_refresh.return_value = {
                    "access_token": "new_access_token",
                    "expires_at": int(time.time()) + 3600,
                }

                store = CredentialStore()
                manager = TokenManager(store)

                result = manager.get_valid_oauth_token()
                assert result == "new_access_token"
                mock_refresh.assert_called_once_with("refresh_token")

    @pytest.mark.unit
    def test_returns_none_when_refresh_fails(self, temp_hopx_dir: Any) -> None:
        """Returns None when token refresh fails."""
        from hopx_cli.auth.credentials import CredentialStore

        with patch("hopx_cli.auth.credentials.keyring") as mock_keyring:
            expires_at = int(time.time()) + 120  # expiring soon
            mock_keyring.get_password.side_effect = lambda _service, key: {
                "default:oauth_access": "old_token",
                "default:oauth_refresh": "refresh_token",
                "default:oauth_expires": str(expires_at),
            }.get(key)

            with patch("hopx_cli.auth.token.refresh_oauth_token") as mock_refresh:
                mock_refresh.side_effect = Exception("Refresh failed")

                store = CredentialStore()
                manager = TokenManager(store)

                result = manager.get_valid_oauth_token()
                assert result is None

    @pytest.mark.unit
    def test_returns_none_when_no_refresh_token(self, temp_hopx_dir: Any) -> None:
        """Returns None when expiring but no refresh token available."""
        from hopx_cli.auth.credentials import CredentialStore

        with patch("hopx_cli.auth.credentials.keyring") as mock:
            expires_at = int(time.time()) + 120  # expiring soon
            mock.get_password.side_effect = lambda _service, key: {
                "default:oauth_access": "old_token",
                "default:oauth_refresh": None,  # No refresh token
                "default:oauth_expires": str(expires_at),
            }.get(key)

            store = CredentialStore()
            manager = TokenManager(store)

            result = manager.get_valid_oauth_token()
            assert result is None

    @pytest.mark.unit
    def test_returns_none_when_no_access_token(self, temp_hopx_dir: Any) -> None:
        """Returns None when no access token in stored data."""
        from hopx_cli.auth.credentials import CredentialStore

        with patch("hopx_cli.auth.credentials.keyring") as mock:
            mock.get_password.side_effect = lambda _service, key: {
                "default:oauth_access": None,
                "default:oauth_refresh": "refresh_token",
                "default:oauth_expires": str(int(time.time()) + 3600),
            }.get(key)

            store = CredentialStore()
            manager = TokenManager(store)

            result = manager.get_valid_oauth_token()
            assert result is None


class TestTokenManagerIsAuthenticated:
    """Tests for TokenManager.is_authenticated()."""

    @pytest.mark.unit
    def test_true_when_has_api_key(
        self, temp_hopx_dir: Any, mock_keyring_with_api_key: MagicMock
    ) -> None:
        """Returns True when API key is available."""
        from hopx_cli.auth.credentials import CredentialStore

        store = CredentialStore()
        manager = TokenManager(store)

        assert manager.is_authenticated() is True

    @pytest.mark.unit
    def test_true_when_has_oauth_token(self, temp_hopx_dir: Any) -> None:
        """Returns True when valid OAuth token is available."""
        from hopx_cli.auth.credentials import CredentialStore

        with patch("hopx_cli.auth.credentials.keyring") as mock:
            future_time = int(time.time()) + 3600
            mock.get_password.side_effect = lambda _service, key: {
                "default:oauth_access": "access_token",
                "default:oauth_refresh": "refresh_token",
                "default:oauth_expires": str(future_time),
            }.get(key)

            store = CredentialStore()
            manager = TokenManager(store)

            assert manager.is_authenticated() is True

    @pytest.mark.unit
    def test_false_when_no_credentials(self, temp_hopx_dir: Any, mock_keyring: MagicMock) -> None:
        """Returns False when no credentials available."""
        from hopx_cli.auth.credentials import CredentialStore

        store = CredentialStore()
        manager = TokenManager(store)

        assert manager.is_authenticated() is False


class TestTokenManagerGetAuthStatus:
    """Tests for TokenManager.get_auth_status()."""

    @pytest.mark.unit
    def test_no_auth_status(self, temp_hopx_dir: Any, mock_keyring: MagicMock) -> None:
        """Returns correct status when not authenticated."""
        from hopx_cli.auth.credentials import CredentialStore

        store = CredentialStore()
        manager = TokenManager(store)

        status = manager.get_auth_status()
        assert status["auth_method"] is None
        assert status["has_api_key"] is False
        assert status["has_oauth"] is False
        assert status["is_authenticated"] is False

    @pytest.mark.unit
    def test_api_key_only_status(
        self, temp_hopx_dir: Any, mock_keyring_with_api_key: MagicMock
    ) -> None:
        """Returns correct status with API key only."""
        from hopx_cli.auth.credentials import CredentialStore

        store = CredentialStore()
        manager = TokenManager(store)

        status = manager.get_auth_status()
        assert status["auth_method"] == "api_key"
        assert status["has_api_key"] is True
        assert status["has_oauth"] is False
        assert status["is_authenticated"] is True
        assert status["api_key_preview"] is not None
        assert "***" in status["api_key_preview"] or "*" in status["api_key_preview"]

    @pytest.mark.unit
    def test_oauth_only_status(self, temp_hopx_dir: Any) -> None:
        """Returns correct status with OAuth token only."""
        from hopx_cli.auth.credentials import CredentialStore

        with patch("hopx_cli.auth.credentials.keyring") as mock:
            future_time = int(time.time()) + 3600
            mock.get_password.side_effect = lambda _service, key: {
                "default:oauth_access": "oauth_access_token",
                "default:oauth_refresh": "refresh_token",
                "default:oauth_expires": str(future_time),
                "default:api_key": None,
            }.get(key)

            store = CredentialStore()
            manager = TokenManager(store)

            status = manager.get_auth_status()
            assert status["auth_method"] == "oauth"
            assert status["has_api_key"] is False
            assert status["has_oauth"] is True
            assert status["is_authenticated"] is True

    @pytest.mark.unit
    def test_both_auth_status(self, temp_hopx_dir: Any) -> None:
        """Returns correct status with both API key and OAuth."""
        from hopx_cli.auth.credentials import CredentialStore

        with patch("hopx_cli.auth.credentials.keyring") as mock:
            future_time = int(time.time()) + 3600
            mock.get_password.side_effect = lambda _service, key: {
                "default:api_key": "hopx_live_key123.secret",
                "default:oauth_access": "oauth_access_token",
                "default:oauth_refresh": "refresh_token",
                "default:oauth_expires": str(future_time),
            }.get(key)

            store = CredentialStore()
            manager = TokenManager(store)

            status = manager.get_auth_status()
            assert status["auth_method"] == "both"
            assert status["has_api_key"] is True
            assert status["has_oauth"] is True
            assert status["is_authenticated"] is True

    @pytest.mark.unit
    def test_api_key_preview_format(self, temp_hopx_dir: Any) -> None:
        """API key preview correctly masks the secret part."""
        from hopx_cli.auth.credentials import CredentialStore

        with patch("hopx_cli.auth.credentials.keyring") as mock:
            mock.get_password.side_effect = lambda _service, key: (
                "hopx_live_abc123.secretpart" if key == "default:api_key" else None
            )

            store = CredentialStore()
            manager = TokenManager(store)

            status = manager.get_auth_status()
            # Should show key ID but mask secret
            assert "abc123" in status["api_key_preview"]
            assert "secretpart" not in status["api_key_preview"]


class TestTokenManagerGetPreferredToken:
    """Tests for TokenManager.get_preferred_token()."""

    @pytest.mark.unit
    def test_prefers_oauth_over_api_key(self, temp_hopx_dir: Any) -> None:
        """OAuth token is preferred over API key."""
        from hopx_cli.auth.credentials import CredentialStore

        with patch("hopx_cli.auth.credentials.keyring") as mock:
            future_time = int(time.time()) + 3600
            mock.get_password.side_effect = lambda _service, key: {
                "default:api_key": "api_key_value",
                "default:oauth_access": "oauth_access_token",
                "default:oauth_refresh": "refresh_token",
                "default:oauth_expires": str(future_time),
            }.get(key)

            store = CredentialStore()
            manager = TokenManager(store)

            result = manager.get_preferred_token()
            assert result == "oauth_access_token"

    @pytest.mark.unit
    def test_falls_back_to_api_key(
        self, temp_hopx_dir: Any, mock_keyring_with_api_key: MagicMock
    ) -> None:
        """Falls back to API key when no OAuth token."""
        from hopx_cli.auth.credentials import CredentialStore

        store = CredentialStore()
        manager = TokenManager(store)

        result = manager.get_preferred_token()
        assert result == "hopx_live_stored.secret"

    @pytest.mark.unit
    def test_returns_none_when_no_tokens(self, temp_hopx_dir: Any, mock_keyring: MagicMock) -> None:
        """Returns None when no tokens available."""
        from hopx_cli.auth.credentials import CredentialStore

        store = CredentialStore()
        manager = TokenManager(store)

        result = manager.get_preferred_token()
        assert result is None
