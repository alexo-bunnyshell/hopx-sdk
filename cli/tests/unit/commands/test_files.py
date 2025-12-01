"""Tests for file operation commands.

Tests cover:
- Files command help text
- List, read, write, delete subcommands
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

runner = CliRunner()


# =============================================================================
# Command Help Tests
# =============================================================================


class TestFilesCommandHelp:
    """Tests for files command help text."""

    @pytest.mark.unit
    def test_files_help(self) -> None:
        """Files command shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["files", "--help"])
        assert result.exit_code == 0
        assert "files" in result.output.lower() or "file" in result.output.lower()

    @pytest.mark.unit
    def test_files_alias_f_works(self) -> None:
        """f alias works for files."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["f", "--help"])
        assert result.exit_code == 0

    @pytest.mark.unit
    def test_files_list_help(self) -> None:
        """Files list subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["files", "list", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output.lower()

    @pytest.mark.unit
    def test_files_read_help(self) -> None:
        """Files read subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["files", "read", "--help"])
        assert result.exit_code == 0
        assert "read" in result.output.lower() or "path" in result.output.lower()

    @pytest.mark.unit
    def test_files_write_help(self) -> None:
        """Files write subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["files", "write", "--help"])
        assert result.exit_code == 0
        assert "write" in result.output.lower() or "path" in result.output.lower()

    @pytest.mark.unit
    def test_files_delete_help(self) -> None:
        """Files delete subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["files", "delete", "--help"])
        assert result.exit_code == 0
        assert "delete" in result.output.lower()
