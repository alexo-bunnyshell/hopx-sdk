"""Tests for prompt helpers.

Tests cover:
- Destructive operation confirmation
- Action confirmation
- Choice prompts
- Text prompts
- Resource summary display
"""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest
from rich.console import Console


class TestConfirmDestructive:
    """Tests for confirm_destructive function."""

    @pytest.mark.unit
    def test_displays_warning_message(self) -> None:
        """Displays warning with message and resource name."""
        from hopx_cli.output.prompts import confirm_destructive

        output = StringIO()
        with patch("hopx_cli.output.prompts.console", Console(file=output, force_terminal=True)):
            with patch("hopx_cli.output.prompts.Confirm.ask", return_value=False):
                confirm_destructive("Delete template", "my-template")

        result = output.getvalue()
        assert "Delete template" in result
        assert "my-template" in result

    @pytest.mark.unit
    def test_displays_details(self) -> None:
        """Displays additional details when provided."""
        from hopx_cli.output.prompts import confirm_destructive

        output = StringIO()
        with patch("hopx_cli.output.prompts.console", Console(file=output, force_terminal=True)):
            with patch("hopx_cli.output.prompts.Confirm.ask", return_value=False):
                confirm_destructive(
                    "Delete template",
                    "my-template",
                    details={"sandboxes_using": 3, "created_at": "2024-01-15"},
                )

        result = output.getvalue()
        assert "Sandboxes Using" in result or "sandboxes" in result.lower()
        assert "3" in result

    @pytest.mark.unit
    def test_returns_user_confirmation(self) -> None:
        """Returns user's confirmation response."""
        from hopx_cli.output.prompts import confirm_destructive

        with patch("hopx_cli.output.prompts.console"):
            with patch("hopx_cli.output.prompts.Confirm.ask", return_value=True):
                result = confirm_destructive("Delete", "resource")
                assert result is True

            with patch("hopx_cli.output.prompts.Confirm.ask", return_value=False):
                result = confirm_destructive("Delete", "resource")
                assert result is False

    @pytest.mark.unit
    def test_default_is_false(self) -> None:
        """Default is False for safety."""
        from hopx_cli.output.prompts import confirm_destructive

        with patch("hopx_cli.output.prompts.console"):
            with patch("hopx_cli.output.prompts.Confirm.ask") as mock_ask:
                mock_ask.return_value = False
                confirm_destructive("Delete", "resource")

                call_kwargs = mock_ask.call_args.kwargs
                assert call_kwargs.get("default") is False


class TestConfirmAction:
    """Tests for confirm_action function."""

    @pytest.mark.unit
    def test_returns_user_confirmation(self) -> None:
        """Returns user's confirmation response."""
        from hopx_cli.output.prompts import confirm_action

        with patch("hopx_cli.output.prompts.Confirm.ask", return_value=True):
            result = confirm_action("Continue?")
            assert result is True

        with patch("hopx_cli.output.prompts.Confirm.ask", return_value=False):
            result = confirm_action("Continue?")
            assert result is False

    @pytest.mark.unit
    def test_default_is_true(self) -> None:
        """Default is True for non-destructive actions."""
        from hopx_cli.output.prompts import confirm_action

        with patch("hopx_cli.output.prompts.Confirm.ask") as mock_ask:
            mock_ask.return_value = True
            confirm_action("Continue?")

            mock_ask.assert_called_once_with("Continue?", default=True)

    @pytest.mark.unit
    def test_custom_default(self) -> None:
        """Accepts custom default value."""
        from hopx_cli.output.prompts import confirm_action

        with patch("hopx_cli.output.prompts.Confirm.ask") as mock_ask:
            mock_ask.return_value = False
            confirm_action("Continue?", default=False)

            mock_ask.assert_called_once_with("Continue?", default=False)


class TestPromptChoice:
    """Tests for prompt_choice function."""

    @pytest.mark.unit
    def test_returns_valid_choice(self) -> None:
        """Returns user's valid choice."""
        from hopx_cli.output.prompts import prompt_choice

        with patch("hopx_cli.output.prompts.Prompt.ask", return_value="python"):
            result = prompt_choice("Language", ["python", "javascript"])
            assert result == "python"

    @pytest.mark.unit
    def test_prompts_until_valid(self) -> None:
        """Prompts until user enters valid choice."""
        from hopx_cli.output.prompts import prompt_choice

        with patch("hopx_cli.output.prompts.console"):
            with patch("hopx_cli.output.prompts.Prompt.ask", side_effect=["invalid", "python"]):
                result = prompt_choice("Language", ["python", "javascript"])
                assert result == "python"

    @pytest.mark.unit
    def test_uses_default(self) -> None:
        """Uses default value when provided."""
        from hopx_cli.output.prompts import prompt_choice

        with patch("hopx_cli.output.prompts.Prompt.ask") as mock_ask:
            mock_ask.return_value = "python"
            prompt_choice("Language", ["python", "javascript"], default="python")

            call_kwargs = mock_ask.call_args.kwargs
            assert call_kwargs.get("default") == "python"


class TestPromptText:
    """Tests for prompt_text function."""

    @pytest.mark.unit
    def test_returns_user_input(self) -> None:
        """Returns user's text input."""
        from hopx_cli.output.prompts import prompt_text

        with patch("hopx_cli.output.prompts.Prompt.ask", return_value="my-sandbox"):
            result = prompt_text("Name")
            assert result == "my-sandbox"

    @pytest.mark.unit
    def test_uses_default(self) -> None:
        """Uses default value when provided."""
        from hopx_cli.output.prompts import prompt_text

        with patch("hopx_cli.output.prompts.Prompt.ask") as mock_ask:
            mock_ask.return_value = "default-name"
            prompt_text("Name", default="default-name")

            call_kwargs = mock_ask.call_args.kwargs
            assert call_kwargs.get("default") == "default-name"

    @pytest.mark.unit
    def test_password_mode(self) -> None:
        """Hides input in password mode."""
        from hopx_cli.output.prompts import prompt_text

        with patch("hopx_cli.output.prompts.Prompt.ask") as mock_ask:
            mock_ask.return_value = "secret"
            prompt_text("Password", password=True)

            call_kwargs = mock_ask.call_args.kwargs
            assert call_kwargs.get("password") is True


class TestShowResourceSummary:
    """Tests for show_resource_summary function."""

    @pytest.mark.unit
    def test_displays_title(self) -> None:
        """Displays summary title."""
        from hopx_cli.output.prompts import show_resource_summary

        output = StringIO()
        with patch("hopx_cli.output.prompts.console", Console(file=output, force_terminal=True)):
            show_resource_summary("Sandbox Created", {"ID": "sb_123"})

        assert "Sandbox Created" in output.getvalue()

    @pytest.mark.unit
    def test_displays_fields(self) -> None:
        """Displays all fields."""
        from hopx_cli.output.prompts import show_resource_summary

        output = StringIO()
        with patch("hopx_cli.output.prompts.console", Console(file=output, force_terminal=True)):
            show_resource_summary(
                "Sandbox Created",
                {"ID": "sb_123", "Template": "python", "Status": "running"},
            )

        result = output.getvalue()
        assert "ID" in result
        assert "sb_123" in result
        assert "Template" in result
        assert "python" in result

    @pytest.mark.unit
    def test_custom_style(self) -> None:
        """Uses custom style color."""
        from hopx_cli.output.prompts import show_resource_summary

        output = StringIO()
        with patch("hopx_cli.output.prompts.console", Console(file=output, force_terminal=True)):
            show_resource_summary("Warning", {"Message": "test"}, style="yellow")

        # Style is applied (hard to verify exact color in output)
        assert "Warning" in output.getvalue()
