"""Tests for code execution commands.

Tests cover:
- Language detection from file extension
- Environment variable parsing
- Output truncation
- Command help text
- Execution result formatting
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer
from typer.testing import CliRunner

runner = CliRunner()


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestDetectLanguageFromFile:
    """Tests for detect_language_from_file helper."""

    @pytest.mark.unit
    def test_detects_python(self) -> None:
        """Detects Python from .py extension."""
        from hopx_cli.commands.run import detect_language_from_file

        assert detect_language_from_file(Path("script.py")) == "python"

    @pytest.mark.unit
    def test_detects_javascript(self) -> None:
        """Detects JavaScript from .js extension."""
        from hopx_cli.commands.run import detect_language_from_file

        assert detect_language_from_file(Path("app.js")) == "javascript"

    @pytest.mark.unit
    def test_detects_javascript_mjs(self) -> None:
        """Detects JavaScript from .mjs extension."""
        from hopx_cli.commands.run import detect_language_from_file

        assert detect_language_from_file(Path("module.mjs")) == "javascript"

    @pytest.mark.unit
    def test_detects_bash(self) -> None:
        """Detects Bash from .sh extension."""
        from hopx_cli.commands.run import detect_language_from_file

        assert detect_language_from_file(Path("deploy.sh")) == "bash"

    @pytest.mark.unit
    def test_detects_bash_extension(self) -> None:
        """Detects Bash from .bash extension."""
        from hopx_cli.commands.run import detect_language_from_file

        assert detect_language_from_file(Path("script.bash")) == "bash"

    @pytest.mark.unit
    def test_detects_go(self) -> None:
        """Detects Go from .go extension."""
        from hopx_cli.commands.run import detect_language_from_file

        assert detect_language_from_file(Path("main.go")) == "go"

    @pytest.mark.unit
    def test_defaults_to_python(self) -> None:
        """Defaults to Python for unknown extensions."""
        from hopx_cli.commands.run import detect_language_from_file

        assert detect_language_from_file(Path("file.unknown")) == "python"
        assert detect_language_from_file(Path("file.txt")) == "python"

    @pytest.mark.unit
    def test_handles_uppercase_extension(self) -> None:
        """Handles uppercase extensions."""
        from hopx_cli.commands.run import detect_language_from_file

        assert detect_language_from_file(Path("script.PY")) == "python"
        assert detect_language_from_file(Path("app.JS")) == "javascript"


class TestParseEnvVars:
    """Tests for parse_env_vars helper."""

    @pytest.mark.unit
    def test_parses_empty(self) -> None:
        """Returns empty dict when no env vars provided."""
        from hopx_cli.commands.run import parse_env_vars

        assert parse_env_vars(None) == {}
        assert parse_env_vars([]) == {}

    @pytest.mark.unit
    def test_parses_single_var(self) -> None:
        """Parses single environment variable."""
        from hopx_cli.commands.run import parse_env_vars

        result = parse_env_vars(["KEY=value"])
        assert result == {"KEY": "value"}

    @pytest.mark.unit
    def test_parses_multiple_vars(self) -> None:
        """Parses multiple environment variables."""
        from hopx_cli.commands.run import parse_env_vars

        result = parse_env_vars(["KEY1=value1", "KEY2=value2"])
        assert result == {"KEY1": "value1", "KEY2": "value2"}

    @pytest.mark.unit
    def test_parses_value_with_equals(self) -> None:
        """Handles values containing equals sign."""
        from hopx_cli.commands.run import parse_env_vars

        result = parse_env_vars(["URL=http://example.com?key=value"])
        assert result["URL"] == "http://example.com?key=value"

    @pytest.mark.unit
    def test_raises_on_invalid_format(self) -> None:
        """Raises BadParameter for invalid format."""
        from hopx_cli.commands.run import parse_env_vars

        with pytest.raises(typer.BadParameter, match="Invalid env var format"):
            parse_env_vars(["INVALID_NO_EQUALS"])


class TestTruncateOutput:
    """Tests for truncate_output helper."""

    @pytest.mark.unit
    def test_returns_empty_unchanged(self) -> None:
        """Returns empty string unchanged."""
        from hopx_cli.commands.run import truncate_output

        text, truncated = truncate_output("")
        assert text == ""
        assert truncated is False

    @pytest.mark.unit
    def test_returns_none_unchanged(self) -> None:
        """Handles None input."""
        from hopx_cli.commands.run import truncate_output

        text, truncated = truncate_output(None)  # type: ignore
        assert text is None
        assert truncated is False

    @pytest.mark.unit
    def test_small_output_unchanged(self) -> None:
        """Returns small output unchanged."""
        from hopx_cli.commands.run import truncate_output

        small_text = "line1\nline2\nline3"
        text, truncated = truncate_output(small_text)
        assert text == small_text
        assert truncated is False

    @pytest.mark.unit
    def test_truncates_large_output(self) -> None:
        """Truncates output exceeding max lines."""
        from hopx_cli.commands.run import truncate_output

        lines = [f"line{i}" for i in range(100)]
        large_text = "\n".join(lines)

        text, truncated = truncate_output(large_text, max_lines=50)

        assert truncated is True
        assert text.count("\n") == 49  # 50 lines = 49 newlines
        assert "line0" in text
        assert "line49" in text
        assert "line99" not in text

    @pytest.mark.unit
    def test_exact_max_lines_not_truncated(self) -> None:
        """Output exactly at max lines is not truncated."""
        from hopx_cli.commands.run import truncate_output

        lines = [f"line{i}" for i in range(50)]
        text_50 = "\n".join(lines)

        text, truncated = truncate_output(text_50, max_lines=50)

        assert truncated is False
        assert text == text_50


class TestLanguageExtensions:
    """Tests for language/extension mappings."""

    @pytest.mark.unit
    def test_language_extensions_mapping(self) -> None:
        """LANGUAGE_EXTENSIONS has expected languages."""
        from hopx_cli.commands.run import LANGUAGE_EXTENSIONS

        assert "python" in LANGUAGE_EXTENSIONS
        assert "javascript" in LANGUAGE_EXTENSIONS
        assert "bash" in LANGUAGE_EXTENSIONS
        assert "go" in LANGUAGE_EXTENSIONS

    @pytest.mark.unit
    def test_extension_to_language_mapping(self) -> None:
        """EXTENSION_TO_LANGUAGE has expected extensions."""
        from hopx_cli.commands.run import EXTENSION_TO_LANGUAGE

        assert EXTENSION_TO_LANGUAGE[".py"] == "python"
        assert EXTENSION_TO_LANGUAGE[".js"] == "javascript"
        assert EXTENSION_TO_LANGUAGE[".sh"] == "bash"
        assert EXTENSION_TO_LANGUAGE[".go"] == "go"


# =============================================================================
# Command Help Tests
# =============================================================================


class TestRunCommandHelp:
    """Tests for run command help text."""

    @pytest.mark.unit
    def test_run_help(self) -> None:
        """Run command shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["run", "--help"])
        assert result.exit_code == 0
        assert "Execute" in result.output or "code" in result.output.lower()

    @pytest.mark.unit
    def test_run_code_help(self) -> None:
        """Run code subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["run", "code", "--help"])
        assert result.exit_code == 0
        assert "sandbox" in result.output.lower() or "code" in result.output.lower()

    @pytest.mark.unit
    def test_run_file_help(self) -> None:
        """Run file subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["run", "file", "--help"])
        assert result.exit_code == 0
        assert "file" in result.output.lower()

    @pytest.mark.unit
    def test_run_command_help(self) -> None:
        """Run command subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["run", "command", "--help"])
        assert result.exit_code == 0
        assert "command" in result.output.lower() or "shell" in result.output.lower()


# =============================================================================
# Execution Result Formatting Tests
# =============================================================================


class TestFormatExecutionResult:
    """Tests for format_execution_result helper."""

    @pytest.mark.unit
    def test_json_format_output(self) -> None:
        """JSON format produces valid JSON."""
        from hopx_cli.commands.run import format_execution_result

        mock_result = MagicMock()
        mock_result.stdout = "Hello, World!"
        mock_result.stderr = ""
        mock_result.exit_code = 0
        mock_result.success = True
        mock_result.execution_time = 0.5
        mock_result.result = None
        mock_result.rich_outputs = []

        with patch("hopx_cli.commands.run.console") as mock_console:
            format_execution_result(mock_result, "json", "python")

            # Should have called print with JSON
            mock_console.print.assert_called_once()
            printed = mock_console.print.call_args[0][0]
            assert "Hello, World!" in printed

    @pytest.mark.unit
    def test_plain_format_output(self) -> None:
        """Plain format outputs stdout directly."""
        from hopx_cli.commands.run import format_execution_result

        mock_result = MagicMock()
        mock_result.stdout = "output text"
        mock_result.stderr = ""

        with patch("hopx_cli.commands.run.console") as mock_console:
            format_execution_result(mock_result, "plain", "python")

            mock_console.print.assert_called()
            call_args = mock_console.print.call_args
            assert "output text" in call_args[0][0]
