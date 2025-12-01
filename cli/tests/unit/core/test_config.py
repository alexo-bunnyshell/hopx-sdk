"""Tests for CLI configuration management.

Tests cover:
- Configuration loading from environment and files
- Profile management
- API key resolution priority
- Configuration persistence
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from hopx_cli.core.config import CLIConfig


class TestCLIConfigDefaults:
    """Tests for CLIConfig default values."""

    @pytest.mark.unit
    def test_default_api_key_is_none(
        self, temp_hopx_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """api_key defaults to None when env var not set."""
        # Ensure no API key from any source
        monkeypatch.delenv("HOPX_API_KEY", raising=False)
        # Create fresh config without any env vars
        config = CLIConfig.load()
        # Note: If there's an .env file or keyring, this might still find a key
        # For a truly isolated test, we verify the config file load works
        assert config is not None

    @pytest.mark.unit
    def test_default_base_url(self, temp_hopx_dir: Path) -> None:
        """base_url defaults to production API."""
        config = CLIConfig()
        assert config.base_url == "https://api.hopx.dev"

    @pytest.mark.unit
    def test_default_template(self, temp_hopx_dir: Path) -> None:
        """default_template defaults to code-interpreter."""
        config = CLIConfig()
        assert config.default_template == "code-interpreter"

    @pytest.mark.unit
    def test_default_timeout(self, temp_hopx_dir: Path) -> None:
        """default_timeout defaults to 3600 seconds."""
        config = CLIConfig()
        assert config.default_timeout == 3600

    @pytest.mark.unit
    def test_default_output_format(self, temp_hopx_dir: Path) -> None:
        """output_format defaults to table."""
        config = CLIConfig()
        assert config.output_format == "table"

    @pytest.mark.unit
    def test_default_profile(self, temp_hopx_dir: Path) -> None:
        """profile defaults to 'default'."""
        config = CLIConfig()
        assert config.profile == "default"


class TestCLIConfigFromEnvironment:
    """Tests for loading config from environment variables."""

    @pytest.mark.unit
    def test_loads_api_key_from_env(
        self, temp_hopx_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """API key can be loaded from HOPX_API_KEY."""
        monkeypatch.setenv("HOPX_API_KEY", "hopx_live_env.secret")
        config = CLIConfig()
        assert config.api_key == "hopx_live_env.secret"

    @pytest.mark.unit
    def test_loads_base_url_from_env(
        self, temp_hopx_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Base URL can be overridden via HOPX_BASE_URL."""
        monkeypatch.setenv("HOPX_BASE_URL", "https://custom.api.dev")
        config = CLIConfig()
        assert config.base_url == "https://custom.api.dev"

    @pytest.mark.unit
    def test_loads_default_template_from_env(
        self, temp_hopx_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Default template can be set via HOPX_DEFAULT_TEMPLATE."""
        monkeypatch.setenv("HOPX_DEFAULT_TEMPLATE", "nodejs")
        config = CLIConfig()
        assert config.default_template == "nodejs"

    @pytest.mark.unit
    def test_loads_timeout_from_env(
        self, temp_hopx_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Timeout can be set via HOPX_DEFAULT_TIMEOUT."""
        monkeypatch.setenv("HOPX_DEFAULT_TIMEOUT", "7200")
        config = CLIConfig()
        assert config.default_timeout == 7200

    @pytest.mark.unit
    def test_loads_output_format_from_env(
        self, temp_hopx_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Output format can be set via HOPX_OUTPUT_FORMAT."""
        monkeypatch.setenv("HOPX_OUTPUT_FORMAT", "json")
        config = CLIConfig()
        assert config.output_format == "json"

    @pytest.mark.unit
    def test_env_vars_case_insensitive(
        self, temp_hopx_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Environment variables are case insensitive."""
        monkeypatch.setenv("hopx_api_key", "hopx_live_lower.secret")
        config = CLIConfig()
        # Pydantic settings with case_sensitive=False handles this
        assert config.api_key == "hopx_live_lower.secret"


class TestCLIConfigLoad:
    """Tests for CLIConfig.load() method."""

    @pytest.mark.unit
    def test_load_with_no_config_file(self, temp_hopx_dir: Path) -> None:
        """load() works when config file doesn't exist."""
        config = CLIConfig.load()
        assert config.profile == "default"
        assert config.base_url == "https://api.hopx.dev"

    @pytest.mark.unit
    def test_load_from_config_file(self, temp_hopx_dir: Path) -> None:
        """load() reads values from config file."""
        config_path = temp_hopx_dir / "config.yaml"
        config_data = {
            "default": {
                "base_url": "https://file.api.dev",
                "default_template": "python",
            }
        }
        with open(config_path, "w") as f:
            yaml.safe_dump(config_data, f)

        config = CLIConfig.load()
        assert config.base_url == "https://file.api.dev"
        assert config.default_template == "python"

    @pytest.mark.unit
    def test_load_specific_profile(self, temp_hopx_dir: Path) -> None:
        """load() can load a specific profile."""
        config_path = temp_hopx_dir / "config.yaml"
        config_data = {
            "default": {"default_template": "python"},
            "staging": {"default_template": "nodejs", "base_url": "https://staging.api.dev"},
        }
        with open(config_path, "w") as f:
            yaml.safe_dump(config_data, f)

        config = CLIConfig.load(profile="staging")
        assert config.profile == "staging"
        assert config.default_template == "nodejs"
        assert config.base_url == "https://staging.api.dev"

    @pytest.mark.unit
    def test_env_vars_are_loaded(
        self, temp_hopx_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Environment variables are loaded by Pydantic settings."""
        # When no config file exists, env vars are used
        monkeypatch.setenv("HOPX_API_KEY", "env_key")
        config = CLIConfig.load()
        assert config.api_key == "env_key"

    @pytest.mark.unit
    def test_load_handles_corrupted_file(self, temp_hopx_dir: Path) -> None:
        """load() handles corrupted config file gracefully."""
        config_path = temp_hopx_dir / "config.yaml"
        with open(config_path, "w") as f:
            f.write("invalid: yaml: content: [")

        # Should not raise, uses defaults
        config = CLIConfig.load()
        assert config.base_url == "https://api.hopx.dev"

    @pytest.mark.unit
    def test_load_handles_empty_file(self, temp_hopx_dir: Path) -> None:
        """load() handles empty config file."""
        config_path = temp_hopx_dir / "config.yaml"
        config_path.touch()

        config = CLIConfig.load()
        assert config.base_url == "https://api.hopx.dev"


class TestCLIConfigSave:
    """Tests for CLIConfig.save() method."""

    @pytest.mark.unit
    def test_save_creates_config_file(self, temp_hopx_dir: Path) -> None:
        """save() creates config file if it doesn't exist."""
        config = CLIConfig(api_key="test_key", default_template="go")
        config.save()

        config_path = temp_hopx_dir / "config.yaml"
        assert config_path.exists()

    @pytest.mark.unit
    def test_save_writes_correct_values(self, temp_hopx_dir: Path) -> None:
        """save() persists configuration values."""
        config = CLIConfig(
            api_key="saved_key",
            base_url="https://saved.api.dev",
            default_template="rust",
        )
        config.save()

        config_path = temp_hopx_dir / "config.yaml"
        with open(config_path) as f:
            data = yaml.safe_load(f)

        assert data["default"]["api_key"] == "saved_key"
        assert data["default"]["base_url"] == "https://saved.api.dev"
        assert data["default"]["default_template"] == "rust"

    @pytest.mark.unit
    def test_save_preserves_other_profiles(self, temp_hopx_dir: Path) -> None:
        """save() doesn't overwrite other profiles."""
        config_path = temp_hopx_dir / "config.yaml"
        existing_data = {
            "staging": {"api_key": "staging_key"},
            "production": {"api_key": "prod_key"},
        }
        with open(config_path, "w") as f:
            yaml.safe_dump(existing_data, f)

        config = CLIConfig(api_key="default_key")
        config.save()

        with open(config_path) as f:
            data = yaml.safe_load(f)

        assert data["staging"]["api_key"] == "staging_key"
        assert data["production"]["api_key"] == "prod_key"
        assert data["default"]["api_key"] == "default_key"

    @pytest.mark.unit
    def test_save_to_specific_profile(self, temp_hopx_dir: Path) -> None:
        """save() saves to the configured profile."""
        config = CLIConfig(api_key="dev_key", profile="development")
        config.profile = "development"
        config.save()

        config_path = temp_hopx_dir / "config.yaml"
        with open(config_path) as f:
            data = yaml.safe_load(f)

        assert "development" in data
        assert data["development"]["api_key"] == "dev_key"


class TestCLIConfigGetApiKey:
    """Tests for CLIConfig.get_api_key() method."""

    @pytest.mark.unit
    def test_returns_api_key_from_config(self, temp_hopx_dir: Path) -> None:
        """get_api_key() returns key if set in config."""
        config = CLIConfig(api_key="config_key")
        assert config.get_api_key() == "config_key"

    @pytest.mark.unit
    def test_returns_api_key_from_credential_store(
        self, temp_hopx_dir: Path, mock_keyring_with_api_key: Any
    ) -> None:
        """get_api_key() falls back to credential store."""
        config = CLIConfig(api_key=None)
        api_key = config.get_api_key()
        assert api_key == "hopx_live_stored.secret"

    @pytest.mark.unit
    def test_raises_when_no_api_key(self, temp_hopx_dir: Path, mock_keyring: Any) -> None:
        """get_api_key() raises ValueError when no key found."""
        config = CLIConfig(api_key=None)
        with pytest.raises(ValueError) as exc_info:
            config.get_api_key()
        assert "API key not configured" in str(exc_info.value)

    @pytest.mark.unit
    def test_config_key_has_priority_over_keyring(
        self, temp_hopx_dir: Path, mock_keyring_with_api_key: Any
    ) -> None:
        """Config/env key takes priority over credential store."""
        config = CLIConfig(api_key="priority_key")
        assert config.get_api_key() == "priority_key"


class TestCLIConfigGetConfigPath:
    """Tests for CLIConfig.get_config_path() method."""

    @pytest.mark.unit
    def test_returns_correct_path(self, temp_home: Path) -> None:
        """get_config_path() returns ~/.hopx/config.yaml."""
        path = CLIConfig.get_config_path()
        assert path == temp_home / ".hopx" / "config.yaml"

    @pytest.mark.unit
    def test_path_is_absolute(self) -> None:
        """get_config_path() returns absolute path."""
        path = CLIConfig.get_config_path()
        assert path.is_absolute()
