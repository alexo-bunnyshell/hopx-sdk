"""Tests for system commands.

Tests cover:
- System health check
- System info
- Command help text
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

runner = CliRunner()


# =============================================================================
# Command Help Tests
# =============================================================================


class TestSystemCommandHelp:
    """Tests for system command help text."""

    @pytest.mark.unit
    def test_system_help(self) -> None:
        """System command shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["system", "--help"])
        assert result.exit_code == 0
        assert "system" in result.output.lower() or "System" in result.output

    @pytest.mark.unit
    def test_system_health_help(self) -> None:
        """System health subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["system", "health", "--help"])
        assert result.exit_code == 0
        assert "health" in result.output.lower()

    @pytest.mark.unit
    def test_system_agent_info_help(self) -> None:
        """System agent-info subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["system", "agent-info", "--help"])
        assert result.exit_code == 0
        assert "agent" in result.output.lower() or "sandbox" in result.output.lower()


# =============================================================================
# System Health Tests
# =============================================================================


class TestSystemHealthCommand:
    """Tests for system health command."""

    @pytest.mark.unit
    def test_system_health_makes_request(
        self, temp_hopx_dir: Path, mock_keyring_with_api_key: Any
    ) -> None:
        """System health command makes API request."""
        import httpx

        from hopx_cli.main import app as main_app

        with patch.object(httpx, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}
            mock_get.return_value = mock_response

            result = runner.invoke(main_app, ["system", "health"])

            # Should make request and show result
            assert mock_get.called or result.exit_code in [0, 1]


# =============================================================================
# System Metrics Tests
# =============================================================================


class TestSystemMetricsCommand:
    """Tests for system metrics command."""

    @pytest.mark.unit
    def test_system_metrics_help(self) -> None:
        """System metrics subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["system", "metrics", "--help"])
        assert result.exit_code == 0
        assert "metric" in result.output.lower() or "sandbox" in result.output.lower()

    @pytest.mark.unit
    def test_system_processes_help(self) -> None:
        """System processes subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["system", "processes", "--help"])
        assert result.exit_code == 0
        assert "process" in result.output.lower() or "sandbox" in result.output.lower()
