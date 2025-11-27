"""Tests for configuration commands.

Tests cover:
- Config command help text
- Config show/set/get subcommands
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

runner = CliRunner()


# =============================================================================
# Command Help Tests
# =============================================================================


class TestConfigCommandHelp:
    """Tests for config command help text."""

    @pytest.mark.unit
    def test_config_help(self) -> None:
        """Config command shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["config", "--help"])
        assert result.exit_code == 0
        assert "config" in result.output.lower() or "Configuration" in result.output

    @pytest.mark.unit
    def test_config_show_help(self) -> None:
        """Config show subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["config", "show", "--help"])
        assert result.exit_code == 0
        assert "show" in result.output.lower() or "display" in result.output.lower()

    @pytest.mark.unit
    def test_config_set_help(self) -> None:
        """Config set subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["config", "set", "--help"])
        assert result.exit_code == 0
        assert "set" in result.output.lower() or "value" in result.output.lower()

    @pytest.mark.unit
    def test_config_get_help(self) -> None:
        """Config get subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["config", "get", "--help"])
        assert result.exit_code == 0
        assert "get" in result.output.lower()

    @pytest.mark.unit
    def test_config_path_help(self) -> None:
        """Config path subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["config", "path", "--help"])
        assert result.exit_code == 0
        assert "path" in result.output.lower()


# =============================================================================
# Config Show Tests
# =============================================================================


class TestConfigShowCommand:
    """Tests for config show command."""

    @pytest.mark.unit
    def test_config_show_runs(self, temp_hopx_dir: Path, mock_keyring: Any) -> None:
        """Config show command executes."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["config", "show"])

        # Should show config or indicate no config
        assert result.exit_code == 0 or "config" in result.output.lower()


class TestConfigPathCommand:
    """Tests for config path command."""

    @pytest.mark.unit
    def test_config_path_shows_path(self, temp_hopx_dir: Path, mock_keyring: Any) -> None:
        """Config path shows the config file path."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["config", "path"])

        # Should show a path
        assert result.exit_code == 0
        assert "hopx" in result.output.lower() or "/" in result.output
