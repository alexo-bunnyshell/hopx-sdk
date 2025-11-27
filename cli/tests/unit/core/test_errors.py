"""Tests for CLI error handling and SDK error mapping.

Tests cover:
- CLI error class hierarchy and exit codes
- SDK error to CLI error mapping
- Error display formatting
- @handle_errors decorator functionality
"""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import hopx_ai.errors as sdk_errors
import pytest

from hopx_cli.core.errors import (
    AuthenticationError,
    CLIError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
    display_error,
    handle_errors,
    map_sdk_error,
)


class TestCLIErrorClasses:
    """Tests for CLI error class hierarchy."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "error_class,expected_code",
        [
            (CLIError, 1),
            (AuthenticationError, 3),
            (NotFoundError, 4),
            (TimeoutError, 5),
            (NetworkError, 6),
            (RateLimitError, 7),
            (ValidationError, 2),
        ],
    )
    def test_exit_codes(self, error_class: type[CLIError], expected_code: int) -> None:
        """Each error class has correct exit code."""
        assert error_class.exit_code == expected_code

    @pytest.mark.unit
    def test_cli_error_stores_message(self) -> None:
        """CLIError stores the error message."""
        error = CLIError("Something went wrong")
        assert error.message == "Something went wrong"
        assert str(error) == "Something went wrong"

    @pytest.mark.unit
    def test_cli_error_stores_suggestion(self) -> None:
        """CLIError stores suggestion for fixing the error."""
        error = CLIError("Failed", suggestion="Try again later")
        assert error.suggestion == "Try again later"

    @pytest.mark.unit
    def test_cli_error_stores_request_id(self) -> None:
        """CLIError stores request ID from API."""
        error = CLIError("Failed", request_id="req_123")
        assert error.request_id == "req_123"

    @pytest.mark.unit
    def test_cli_error_optional_fields_default_to_none(self) -> None:
        """Optional fields default to None."""
        error = CLIError("Failed")
        assert error.suggestion is None
        assert error.request_id is None


class TestMapSdkError:
    """Tests for map_sdk_error function."""

    @pytest.mark.unit
    def test_maps_authentication_error(self, sdk_auth_error: Any) -> None:
        """SDK AuthenticationError maps to CLI AuthenticationError."""
        result = map_sdk_error(sdk_auth_error)
        assert isinstance(result, AuthenticationError)
        assert result.exit_code == 3
        assert "Invalid API key" in result.message
        assert result.suggestion is not None
        assert "hopx auth" in result.suggestion

    @pytest.mark.unit
    def test_maps_token_expired_error(self) -> None:
        """SDK TokenExpiredError maps to CLI AuthenticationError."""
        sdk_error = sdk_errors.TokenExpiredError(message="Token expired")
        result = map_sdk_error(sdk_error)
        assert isinstance(result, AuthenticationError)
        assert result.exit_code == 3

    @pytest.mark.unit
    def test_maps_not_found_error(self, sdk_not_found_error: Any) -> None:
        """SDK NotFoundError maps to CLI NotFoundError."""
        result = map_sdk_error(sdk_not_found_error)
        assert isinstance(result, NotFoundError)
        assert result.exit_code == 4
        assert "not found" in result.message.lower()

    @pytest.mark.unit
    def test_maps_template_not_found_with_suggestion(
        self, sdk_template_not_found_error: Any
    ) -> None:
        """SDK TemplateNotFoundError maps with suggested template."""
        result = map_sdk_error(sdk_template_not_found_error)
        assert isinstance(result, NotFoundError)
        assert result.exit_code == 4
        assert "python" in result.suggestion  # suggested template

    @pytest.mark.unit
    def test_maps_template_not_found_with_available_list(self) -> None:
        """SDK TemplateNotFoundError shows available templates."""
        sdk_error = sdk_errors.TemplateNotFoundError(
            template_name="invalid",
            available_templates=["python", "nodejs", "go"],
        )
        result = map_sdk_error(sdk_error)
        assert isinstance(result, NotFoundError)
        assert "python" in result.suggestion
        assert "nodejs" in result.suggestion

    @pytest.mark.unit
    def test_maps_timeout_error(self, sdk_timeout_error: Any) -> None:
        """SDK TimeoutError maps to CLI TimeoutError."""
        result = map_sdk_error(sdk_timeout_error)
        assert isinstance(result, TimeoutError)
        assert result.exit_code == 5
        assert "--timeout" in result.suggestion

    @pytest.mark.unit
    def test_maps_network_error(self, sdk_network_error: Any) -> None:
        """SDK NetworkError maps to CLI NetworkError."""
        result = map_sdk_error(sdk_network_error)
        assert isinstance(result, NetworkError)
        assert result.exit_code == 6
        assert "network" in result.suggestion.lower()

    @pytest.mark.unit
    def test_maps_rate_limit_error(self, sdk_rate_limit_error: Any) -> None:
        """SDK RateLimitError maps to CLI RateLimitError."""
        result = map_sdk_error(sdk_rate_limit_error)
        assert isinstance(result, RateLimitError)
        assert result.exit_code == 7
        assert "60" in result.suggestion  # retry_after

    @pytest.mark.unit
    def test_maps_rate_limit_without_retry_after(self) -> None:
        """RateLimitError without retry_after still maps correctly."""
        sdk_error = sdk_errors.RateLimitError(
            message="Rate limited",
            status_code=429,
        )
        result = map_sdk_error(sdk_error)
        assert isinstance(result, RateLimitError)
        assert "Rate limit" in result.suggestion

    @pytest.mark.unit
    def test_maps_validation_error(self, sdk_validation_error: Any) -> None:
        """SDK ValidationError maps to CLI ValidationError."""
        result = map_sdk_error(sdk_validation_error)
        assert isinstance(result, ValidationError)
        assert result.exit_code == 2
        assert "template" in result.message  # field name

    @pytest.mark.unit
    def test_maps_validation_error_without_field(self) -> None:
        """ValidationError without field still maps correctly."""
        sdk_error = sdk_errors.ValidationError(message="Invalid input")
        result = map_sdk_error(sdk_error)
        assert isinstance(result, ValidationError)
        assert result.exit_code == 2

    @pytest.mark.unit
    def test_maps_resource_limit_error(self) -> None:
        """SDK ResourceLimitError maps to CLI error with upgrade suggestion."""
        sdk_error = sdk_errors.ResourceLimitError(
            message="Sandbox limit reached",
            upgrade_url="https://hopx.ai/upgrade",
        )
        result = map_sdk_error(sdk_error)
        assert isinstance(result, CLIError)
        assert "upgrade" in result.suggestion.lower()

    @pytest.mark.unit
    def test_maps_template_build_error(self) -> None:
        """SDK TemplateBuildError maps with suggestion."""
        sdk_error = sdk_errors.TemplateBuildError(
            message="Build failed",
        )
        result = map_sdk_error(sdk_error)
        assert isinstance(result, CLIError)
        assert "build" in result.suggestion.lower() or "dockerfile" in result.suggestion.lower()

    @pytest.mark.unit
    def test_maps_sandbox_expired_error(self) -> None:
        """SDK SandboxExpiredError maps with create suggestion."""
        sdk_error = sdk_errors.SandboxExpiredError(
            message="Sandbox has expired",
        )
        result = map_sdk_error(sdk_error)
        assert isinstance(result, CLIError)
        assert "sandbox create" in result.suggestion

    @pytest.mark.unit
    def test_maps_desktop_not_available_error(self) -> None:
        """SDK DesktopNotAvailableError maps correctly."""
        sdk_error = sdk_errors.DesktopNotAvailableError(
            message="Desktop not available",
            missing_dependencies=["playwright"],
        )
        result = map_sdk_error(sdk_error)
        assert isinstance(result, CLIError)
        # Just check that it maps to a CLI error
        assert result.exit_code == 1

    @pytest.mark.unit
    def test_maps_generic_hopx_error(self) -> None:
        """Generic HopxError maps to base CLIError."""
        sdk_error = sdk_errors.HopxError(message="Unknown error occurred")
        result = map_sdk_error(sdk_error)
        assert isinstance(result, CLIError)
        assert result.exit_code == 1

    @pytest.mark.unit
    def test_preserves_request_id(self) -> None:
        """Request ID is preserved in mapping."""
        sdk_error = sdk_errors.NotFoundError(
            message="Not found",
            request_id="req_abc123",
        )
        result = map_sdk_error(sdk_error)
        assert result.request_id == "req_abc123"


class TestDisplayError:
    """Tests for display_error function."""

    @pytest.mark.unit
    def test_displays_error_message(self) -> None:
        """display_error outputs error message."""
        error = CLIError("Test error message")
        with patch("hopx_cli.core.errors.console") as mock_console:
            display_error(error)
            mock_console.print.assert_called_once()
            # Check panel was created with error content
            call_args = mock_console.print.call_args
            assert call_args is not None

    @pytest.mark.unit
    def test_displays_request_id_when_present(self) -> None:
        """display_error includes request ID."""
        error = CLIError("Test error", request_id="req_test123")
        with patch("hopx_cli.core.errors.console") as mock_console:
            display_error(error)
            mock_console.print.assert_called()

    @pytest.mark.unit
    def test_displays_suggestion_when_present(self) -> None:
        """display_error includes suggestion."""
        error = CLIError("Test error", suggestion="Try this fix")
        with patch("hopx_cli.core.errors.console") as mock_console:
            display_error(error)
            mock_console.print.assert_called()


class TestHandleErrorsDecorator:
    """Tests for @handle_errors decorator."""

    @pytest.mark.unit
    def test_passes_through_on_success(self) -> None:
        """Decorated function returns normally on success."""

        @handle_errors
        def successful_func() -> str:
            return "success"

        result = successful_func()
        assert result == "success"

    @pytest.mark.unit
    def test_catches_keyboard_interrupt(self) -> None:
        """KeyboardInterrupt exits with code 130."""

        @handle_errors
        def interrupted_func() -> None:
            raise KeyboardInterrupt()

        with patch("hopx_cli.core.errors.console"):
            with pytest.raises(SystemExit) as exc_info:
                interrupted_func()
            assert exc_info.value.code == 130

    @pytest.mark.unit
    def test_catches_cli_error(self) -> None:
        """CLIError is displayed and exits with correct code."""

        @handle_errors
        def failing_func() -> None:
            raise AuthenticationError("Auth failed")

        with patch("hopx_cli.core.errors.console"):
            with pytest.raises(SystemExit) as exc_info:
                failing_func()
            assert exc_info.value.code == 3

    @pytest.mark.unit
    def test_catches_sdk_error(self) -> None:
        """SDK error is mapped and exits with correct code."""

        @handle_errors
        def sdk_failing_func() -> None:
            raise sdk_errors.NotFoundError(message="Not found")

        with patch("hopx_cli.core.errors.console"):
            with pytest.raises(SystemExit) as exc_info:
                sdk_failing_func()
            assert exc_info.value.code == 4

    @pytest.mark.unit
    def test_catches_unexpected_error(self) -> None:
        """Unexpected error exits with code 1."""

        @handle_errors
        def unexpected_func() -> None:
            raise RuntimeError("Unexpected!")

        with patch("hopx_cli.core.errors.console"):
            with pytest.raises(SystemExit) as exc_info:
                unexpected_func()
            assert exc_info.value.code == 1

    @pytest.mark.unit
    def test_verbose_shows_traceback(self) -> None:
        """Verbose mode shows traceback on unexpected error."""

        @handle_errors
        def error_func(verbose: bool = False) -> None:
            raise RuntimeError("Unexpected!")

        with patch("hopx_cli.core.errors.console") as mock_console:
            with pytest.raises(SystemExit):
                error_func(verbose=True)
            # Check that traceback was printed
            assert mock_console.print.call_count >= 2

    @pytest.mark.unit
    def test_preserves_function_metadata(self) -> None:
        """Decorator preserves function name and docstring."""

        @handle_errors
        def documented_func() -> None:
            """This is the docstring."""
            pass

        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "This is the docstring."

    @pytest.mark.unit
    def test_passes_args_to_function(self) -> None:
        """Decorator passes arguments correctly."""

        @handle_errors
        def func_with_args(a: int, b: str, c: bool = False) -> tuple[int, str, bool]:
            return (a, b, c)

        result = func_with_args(1, "test", c=True)
        assert result == (1, "test", True)
