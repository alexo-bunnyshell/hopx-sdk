"""Tests for credential storage.

Tests cover:
- API key storage and retrieval
- OAuth token storage and retrieval
- Keyring integration with file fallback
- Multi-profile support
- File permission handling
"""

from __future__ import annotations

import os
import stat
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from hopx_cli.auth.credentials import KEYRING_SERVICE, CredentialStore


class TestCredentialStoreInit:
    """Tests for CredentialStore initialization."""

    @pytest.mark.unit
    def test_default_profile(self, temp_hopx_dir: Path) -> None:
        """Default profile is 'default'."""
        store = CredentialStore()
        assert store.profile == "default"

    @pytest.mark.unit
    def test_custom_profile(self, temp_hopx_dir: Path) -> None:
        """Can initialize with custom profile."""
        store = CredentialStore(profile="staging")
        assert store.profile == "staging"

    @pytest.mark.unit
    def test_config_dir_is_hopx(self, temp_home: Path) -> None:
        """Config directory is ~/.hopx."""
        store = CredentialStore()
        assert store.config_dir == temp_home / ".hopx"

    @pytest.mark.unit
    def test_credentials_file_path(self, temp_home: Path) -> None:
        """Credentials file is ~/.hopx/credentials.yaml."""
        store = CredentialStore()
        assert store.credentials_file == temp_home / ".hopx" / "credentials.yaml"


class TestCredentialStoreApiKey:
    """Tests for API key storage and retrieval."""

    @pytest.mark.unit
    def test_store_api_key_to_keyring(self, temp_hopx_dir: Path, mock_keyring: MagicMock) -> None:
        """API key is stored in keyring when available."""
        store = CredentialStore()
        store.store_api_key("hopx_live_test.secret")

        mock_keyring.set_password.assert_called_once_with(
            KEYRING_SERVICE, "default:api_key", "hopx_live_test.secret"
        )

    @pytest.mark.unit
    def test_store_api_key_falls_back_to_file(
        self, temp_hopx_dir: Path, mock_keyring_unavailable: MagicMock
    ) -> None:
        """API key is stored in file when keyring unavailable."""
        store = CredentialStore()
        store.store_api_key("hopx_live_test.secret")

        # Check file was created
        assert store.credentials_file.exists()
        with open(store.credentials_file) as f:
            data = yaml.safe_load(f)
        assert data["default"]["api_key"] == "hopx_live_test.secret"

    @pytest.mark.unit
    def test_store_api_key_without_keyring(
        self, temp_hopx_dir: Path, mock_keyring: MagicMock
    ) -> None:
        """Can explicitly store to file instead of keyring."""
        store = CredentialStore()
        store.store_api_key("hopx_live_test.secret", use_keyring=False)

        # Keyring should not be called
        mock_keyring.set_password.assert_not_called()
        # File should be created
        assert store.credentials_file.exists()

    @pytest.mark.unit
    def test_get_api_key_from_keyring(
        self, temp_hopx_dir: Path, mock_keyring_with_api_key: MagicMock
    ) -> None:
        """API key is retrieved from keyring."""
        store = CredentialStore()
        key = store.get_api_key()
        assert key == "hopx_live_stored.secret"

    @pytest.mark.unit
    def test_get_api_key_from_file(self, temp_hopx_dir: Path, mock_keyring: MagicMock) -> None:
        """API key is retrieved from file when not in keyring."""
        # Write key to file
        creds_file = temp_hopx_dir / "credentials.yaml"
        with open(creds_file, "w") as f:
            yaml.safe_dump({"default": {"api_key": "file_key"}}, f)

        store = CredentialStore()
        key = store.get_api_key()
        assert key == "file_key"

    @pytest.mark.unit
    def test_get_api_key_from_env(
        self, temp_hopx_dir: Path, mock_keyring: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """API key falls back to HOPX_API_KEY env var."""
        monkeypatch.setenv("HOPX_API_KEY", "env_key")
        store = CredentialStore()
        key = store.get_api_key()
        assert key == "env_key"

    @pytest.mark.unit
    def test_get_api_key_keyring_priority(
        self,
        temp_hopx_dir: Path,
        mock_keyring_with_api_key: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Keyring has priority over file and env."""
        # Set up all sources
        creds_file = temp_hopx_dir / "credentials.yaml"
        with open(creds_file, "w") as f:
            yaml.safe_dump({"default": {"api_key": "file_key"}}, f)
        monkeypatch.setenv("HOPX_API_KEY", "env_key")

        store = CredentialStore()
        key = store.get_api_key()
        # Should get from keyring first
        assert key == "hopx_live_stored.secret"

    @pytest.mark.unit
    def test_get_api_key_returns_none_when_not_found(
        self, temp_hopx_dir: Path, mock_keyring: MagicMock
    ) -> None:
        """Returns None when API key not found anywhere."""
        store = CredentialStore()
        key = store.get_api_key()
        assert key is None


class TestCredentialStoreOAuthToken:
    """Tests for OAuth token storage and retrieval."""

    @pytest.mark.unit
    def test_store_oauth_token_to_keyring(
        self, temp_hopx_dir: Path, mock_keyring: MagicMock
    ) -> None:
        """OAuth token is stored in keyring."""
        store = CredentialStore()
        token = {
            "access_token": "access123",
            "refresh_token": "refresh456",
            "expires_at": 1700000000,
        }
        store.store_oauth_token(token)

        assert mock_keyring.set_password.call_count == 3

    @pytest.mark.unit
    def test_store_oauth_token_requires_access_token(
        self, temp_hopx_dir: Path, mock_keyring: MagicMock
    ) -> None:
        """Raises error if access_token missing."""
        store = CredentialStore()
        with pytest.raises(ValueError, match="access_token"):
            store.store_oauth_token({"refresh_token": "refresh456"})

    @pytest.mark.unit
    def test_store_oauth_token_falls_back_to_file(
        self, temp_hopx_dir: Path, mock_keyring_unavailable: MagicMock
    ) -> None:
        """OAuth token is stored in file when keyring unavailable."""
        store = CredentialStore()
        token = {"access_token": "access123", "refresh_token": "refresh456"}
        store.store_oauth_token(token)

        assert store.credentials_file.exists()
        with open(store.credentials_file) as f:
            data = yaml.safe_load(f)
        assert data["default"]["oauth_token"]["access_token"] == "access123"

    @pytest.mark.unit
    def test_get_oauth_token_from_keyring(self, temp_hopx_dir: Path) -> None:
        """OAuth token is retrieved from keyring."""
        with patch("hopx_cli.auth.credentials.keyring") as mock:
            mock.get_password.side_effect = lambda _service, key: {
                "default:oauth_access": "access123",
                "default:oauth_refresh": "refresh456",
                "default:oauth_expires": "1700000000",
            }.get(key)

            store = CredentialStore()
            token = store.get_oauth_token()

            assert token is not None
            assert token["access_token"] == "access123"
            assert token["refresh_token"] == "refresh456"
            assert token["expires_at"] == 1700000000

    @pytest.mark.unit
    def test_get_oauth_token_from_file(self, temp_hopx_dir: Path, mock_keyring: MagicMock) -> None:
        """OAuth token is retrieved from file."""
        creds_file = temp_hopx_dir / "credentials.yaml"
        token_data = {
            "access_token": "file_access",
            "refresh_token": "file_refresh",
        }
        with open(creds_file, "w") as f:
            yaml.safe_dump({"default": {"oauth_token": token_data}}, f)

        store = CredentialStore()
        token = store.get_oauth_token()
        assert token == token_data

    @pytest.mark.unit
    def test_get_oauth_token_returns_none_when_not_found(
        self, temp_hopx_dir: Path, mock_keyring: MagicMock
    ) -> None:
        """Returns None when OAuth token not found."""
        store = CredentialStore()
        token = store.get_oauth_token()
        assert token is None


class TestCredentialStoreClear:
    """Tests for clearing credentials."""

    @pytest.mark.unit
    def test_clear_removes_from_keyring(self, temp_hopx_dir: Path, mock_keyring: MagicMock) -> None:
        """clear() removes all credentials from keyring."""
        store = CredentialStore()
        store.clear()

        # Should attempt to delete all credential types
        assert mock_keyring.delete_password.call_count >= 3

    @pytest.mark.unit
    def test_clear_removes_from_file(self, temp_hopx_dir: Path, mock_keyring: MagicMock) -> None:
        """clear() removes profile from credentials file."""
        # Create credentials file
        creds_file = temp_hopx_dir / "credentials.yaml"
        with open(creds_file, "w") as f:
            yaml.safe_dump(
                {
                    "default": {"api_key": "key1"},
                    "staging": {"api_key": "key2"},
                },
                f,
            )

        store = CredentialStore(profile="default")
        store.clear()

        # Default profile should be removed, staging should remain
        with open(creds_file) as f:
            data = yaml.safe_load(f)
        assert "default" not in data
        assert "staging" in data

    @pytest.mark.unit
    def test_clear_handles_missing_file(self, temp_hopx_dir: Path, mock_keyring: MagicMock) -> None:
        """clear() handles missing credentials file gracefully."""
        store = CredentialStore()
        # Should not raise
        store.clear()


class TestCredentialStoreMultiProfile:
    """Tests for multi-profile support."""

    @pytest.mark.unit
    def test_different_profiles_isolated(
        self, temp_hopx_dir: Path, mock_keyring_unavailable: MagicMock
    ) -> None:
        """Different profiles have isolated credentials."""
        store1 = CredentialStore(profile="profile1")
        store1.store_api_key("key1")

        store2 = CredentialStore(profile="profile2")
        store2.store_api_key("key2")

        # Each profile should have its own key
        assert store1.get_api_key() == "key1"
        assert store2.get_api_key() == "key2"

    @pytest.mark.unit
    def test_keyring_uses_profile_prefix(
        self, temp_hopx_dir: Path, mock_keyring: MagicMock
    ) -> None:
        """Keyring keys are prefixed with profile name."""
        store = CredentialStore(profile="staging")
        store.store_api_key("staging_key")

        mock_keyring.set_password.assert_called_once_with(
            KEYRING_SERVICE, "staging:api_key", "staging_key"
        )


class TestCredentialStoreFilePermissions:
    """Tests for file permission handling."""

    @pytest.mark.unit
    def test_credentials_file_has_restricted_permissions(
        self, temp_hopx_dir: Path, mock_keyring_unavailable: MagicMock
    ) -> None:
        """Credentials file has 0600 permissions."""
        store = CredentialStore()
        store.store_api_key("secret_key")

        file_stat = os.stat(store.credentials_file)
        # Check owner read/write only (0600)
        expected_mode = stat.S_IRUSR | stat.S_IWUSR
        actual_mode = file_stat.st_mode & 0o777
        assert actual_mode == expected_mode


class TestCredentialStoreClearAllProfiles:
    """Tests for clear_all_profiles class method."""

    @pytest.mark.unit
    def test_clear_all_profiles_removes_file(
        self, temp_hopx_dir: Path, mock_keyring: MagicMock
    ) -> None:
        """clear_all_profiles() removes the credentials file."""
        creds_file = temp_hopx_dir / "credentials.yaml"
        with open(creds_file, "w") as f:
            yaml.safe_dump({"default": {"api_key": "key1"}}, f)

        CredentialStore.clear_all_profiles()

        assert not creds_file.exists()

    @pytest.mark.unit
    def test_clear_all_profiles_returns_cleared_profiles(self, temp_hopx_dir: Path) -> None:
        """clear_all_profiles() returns list of cleared profiles."""
        with patch("hopx_cli.auth.credentials.keyring") as mock:
            mock.get_password.side_effect = lambda _service, key: (
                "key" if key == "default:api_key" else None
            )
            mock.delete_password.return_value = None

            cleared = CredentialStore.clear_all_profiles()
            assert "default" in cleared
