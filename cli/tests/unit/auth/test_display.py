"""Tests for authentication display utilities.

Tests cover:
- Auth URL display with QR codes
- Headless instructions display
- Callback URL prompting
- Success and error message display
"""

from __future__ import annotations

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console


class TestShowAuthUrl:
    """Tests for show_auth_url function."""

    @pytest.mark.unit
    def test_displays_url(self) -> None:
        """Displays the authentication URL."""
        from hopx_cli.auth.display import show_auth_url

        output = StringIO()
        with patch("hopx_cli.auth.display.console", Console(file=output, force_terminal=True)):
            with patch("hopx_cli.auth.display.pyperclip.copy"):
                with patch("hopx_cli.auth.display._print_qr_code"):
                    show_auth_url("https://auth.example.com", show_qr=False)

        assert "https://auth.example.com" in output.getvalue()

    @pytest.mark.unit
    def test_displays_title(self) -> None:
        """Displays the title when provided."""
        from hopx_cli.auth.display import show_auth_url

        output = StringIO()
        with patch("hopx_cli.auth.display.console", Console(file=output, force_terminal=True)):
            with patch("hopx_cli.auth.display.pyperclip.copy"):
                with patch("hopx_cli.auth.display._print_qr_code"):
                    show_auth_url("https://auth.example.com", title="Login", show_qr=False)

        assert "Login" in output.getvalue()

    @pytest.mark.unit
    def test_copies_to_clipboard_when_enabled(self) -> None:
        """Copies URL to clipboard when auto_copy=True."""
        from hopx_cli.auth.display import show_auth_url

        with patch("hopx_cli.auth.display.console"):
            with patch("hopx_cli.auth.display.pyperclip.copy") as mock_copy:
                with patch("hopx_cli.auth.display._print_qr_code"):
                    show_auth_url("https://auth.example.com", auto_copy=True, show_qr=False)

        mock_copy.assert_called_once_with("https://auth.example.com")

    @pytest.mark.unit
    def test_handles_clipboard_failure(self) -> None:
        """Handles clipboard failure gracefully."""
        from hopx_cli.auth.display import show_auth_url

        with patch("hopx_cli.auth.display.console"):
            with patch(
                "hopx_cli.auth.display.pyperclip.copy", side_effect=Exception("No clipboard")
            ):
                with patch("hopx_cli.auth.display._print_qr_code"):
                    # Should not raise
                    show_auth_url("https://auth.example.com", auto_copy=True, show_qr=False)

    @pytest.mark.unit
    def test_shows_qr_code_when_enabled(self) -> None:
        """Shows QR code when show_qr=True."""
        from hopx_cli.auth.display import show_auth_url

        with patch("hopx_cli.auth.display.console"):
            with patch("hopx_cli.auth.display.pyperclip.copy"):
                with patch("hopx_cli.auth.display._print_qr_code") as mock_qr:
                    show_auth_url("https://auth.example.com", show_qr=True)

        mock_qr.assert_called_once_with("https://auth.example.com")

    @pytest.mark.unit
    def test_skips_qr_code_when_disabled(self) -> None:
        """Skips QR code when show_qr=False."""
        from hopx_cli.auth.display import show_auth_url

        with patch("hopx_cli.auth.display.console"):
            with patch("hopx_cli.auth.display.pyperclip.copy"):
                with patch("hopx_cli.auth.display._print_qr_code") as mock_qr:
                    show_auth_url("https://auth.example.com", show_qr=False)

        mock_qr.assert_not_called()


class TestPrintQrCode:
    """Tests for _print_qr_code function."""

    @pytest.mark.unit
    def test_generates_qr_code(self) -> None:
        """Generates and prints QR code."""
        from hopx_cli.auth.display import _print_qr_code

        mock_console = MagicMock()
        with patch("hopx_cli.auth.display.console", mock_console):
            _print_qr_code("https://example.com")

        # Should have printed multiple lines (QR code)
        assert mock_console.print.call_count > 0

    @pytest.mark.unit
    def test_handles_qr_generation_failure(self) -> None:
        """Handles QR code generation failure gracefully."""
        from hopx_cli.auth.display import _print_qr_code

        with patch("hopx_cli.auth.display.qrcode.QRCode", side_effect=Exception("QR failed")):
            with patch("hopx_cli.auth.display.console"):
                # Should not raise
                _print_qr_code("https://example.com")


class TestShowHeadlessInstructions:
    """Tests for show_headless_instructions function."""

    @pytest.mark.unit
    def test_displays_instructions(self) -> None:
        """Displays headless callback instructions."""
        from hopx_cli.auth.display import show_headless_instructions

        output = StringIO()
        with patch("hopx_cli.auth.display.console", Console(file=output, force_terminal=True)):
            show_headless_instructions()

        result = output.getvalue()
        assert "connection refused" in result.lower() or "browser" in result.lower()


class TestPromptCallbackUrl:
    """Tests for prompt_callback_url function."""

    @pytest.mark.unit
    def test_returns_user_input(self) -> None:
        """Returns the URL entered by user."""
        from hopx_cli.auth.display import prompt_callback_url

        mock_console = MagicMock()
        mock_console.input.return_value = "  https://callback.example.com  "

        with patch("hopx_cli.auth.display.console", mock_console):
            result = prompt_callback_url()

        assert result == "https://callback.example.com"

    @pytest.mark.unit
    def test_raises_on_keyboard_interrupt(self) -> None:
        """Raises RuntimeError when user cancels."""
        from hopx_cli.auth.display import prompt_callback_url

        mock_console = MagicMock()
        mock_console.input.side_effect = KeyboardInterrupt()

        with patch("hopx_cli.auth.display.console", mock_console):
            with pytest.raises(RuntimeError, match="cancelled"):
                prompt_callback_url()

    @pytest.mark.unit
    def test_raises_on_eof(self) -> None:
        """Raises RuntimeError on EOF."""
        from hopx_cli.auth.display import prompt_callback_url

        mock_console = MagicMock()
        mock_console.input.side_effect = EOFError()

        with patch("hopx_cli.auth.display.console", mock_console):
            with pytest.raises(RuntimeError, match="cancelled"):
                prompt_callback_url()


class TestShowSuccess:
    """Tests for show_success function."""

    @pytest.mark.unit
    def test_displays_success_message(self) -> None:
        """Displays success message with checkmark."""
        from hopx_cli.auth.display import show_success

        output = StringIO()
        with patch("hopx_cli.auth.display.console", Console(file=output, force_terminal=True)):
            show_success("Login successful!")

        result = output.getvalue()
        assert "Login successful!" in result

    @pytest.mark.unit
    def test_displays_default_message(self) -> None:
        """Displays default message when none provided."""
        from hopx_cli.auth.display import show_success

        output = StringIO()
        with patch("hopx_cli.auth.display.console", Console(file=output, force_terminal=True)):
            show_success()

        result = output.getvalue()
        assert "successful" in result.lower()


class TestShowError:
    """Tests for show_error function."""

    @pytest.mark.unit
    def test_displays_error_message(self) -> None:
        """Displays error message with X mark."""
        from hopx_cli.auth.display import show_error

        output = StringIO()
        with patch("hopx_cli.auth.display.console", Console(file=output, force_terminal=True)):
            show_error("Authentication failed")

        result = output.getvalue()
        assert "Authentication failed" in result


class TestShowProgress:
    """Tests for show_progress function."""

    @pytest.mark.unit
    def test_returns_spinner(self) -> None:
        """Returns a Spinner instance."""
        from hopx_cli.auth.display import show_progress
        from hopx_cli.output import Spinner

        with patch("hopx_cli.output.progress.Live"):
            result = show_progress("Loading...")

        assert isinstance(result, Spinner)
