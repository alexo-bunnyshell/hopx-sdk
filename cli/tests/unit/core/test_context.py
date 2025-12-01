"""Tests for CLI context and runtime state management.

Tests cover:
- OutputFormat enum values
- CLIContext initialization and configuration
- Output format detection methods
- State management
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from hopx_cli.core.context import CLIContext, OutputFormat


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    @pytest.mark.unit
    def test_table_format_value(self) -> None:
        """TABLE format has correct value."""
        assert OutputFormat.TABLE.value == "table"

    @pytest.mark.unit
    def test_json_format_value(self) -> None:
        """JSON format has correct value."""
        assert OutputFormat.JSON.value == "json"

    @pytest.mark.unit
    def test_plain_format_value(self) -> None:
        """PLAIN format has correct value."""
        assert OutputFormat.PLAIN.value == "plain"

    @pytest.mark.unit
    def test_format_from_string(self) -> None:
        """OutputFormat can be created from string."""
        assert OutputFormat("table") == OutputFormat.TABLE
        assert OutputFormat("json") == OutputFormat.JSON
        assert OutputFormat("plain") == OutputFormat.PLAIN

    @pytest.mark.unit
    def test_format_is_string_enum(self) -> None:
        """OutputFormat inherits from str."""
        assert isinstance(OutputFormat.TABLE, str)
        assert OutputFormat.TABLE == "table"


class TestCLIContextInit:
    """Tests for CLIContext initialization."""

    @pytest.mark.unit
    def test_init_with_defaults(self, temp_hopx_dir: Any) -> None:
        """CLIContext initializes with default values."""
        ctx = CLIContext()
        assert ctx.verbose is False
        assert ctx.quiet is False
        assert ctx.no_color is False
        assert ctx.config is not None

    @pytest.mark.unit
    def test_init_with_custom_config(self, mock_config: MagicMock) -> None:
        """CLIContext accepts custom config."""
        ctx = CLIContext(config=mock_config)
        assert ctx.config is mock_config

    @pytest.mark.unit
    def test_init_with_output_format(self, mock_config: MagicMock) -> None:
        """CLIContext accepts output format parameter."""
        ctx = CLIContext(config=mock_config, output_format=OutputFormat.JSON)
        assert ctx.output_format == OutputFormat.JSON

    @pytest.mark.unit
    def test_init_output_format_from_config(self, mock_config: MagicMock) -> None:
        """CLIContext uses config output_format when not specified."""
        mock_config.output_format = "json"
        ctx = CLIContext(config=mock_config)
        assert ctx.output_format == OutputFormat.JSON

    @pytest.mark.unit
    def test_init_with_verbose(self, mock_config: MagicMock) -> None:
        """CLIContext accepts verbose parameter."""
        ctx = CLIContext(config=mock_config, verbose=True)
        assert ctx.verbose is True

    @pytest.mark.unit
    def test_init_with_quiet(self, mock_config: MagicMock) -> None:
        """CLIContext accepts quiet parameter."""
        ctx = CLIContext(config=mock_config, quiet=True)
        assert ctx.quiet is True

    @pytest.mark.unit
    def test_init_with_no_color(self, mock_config: MagicMock) -> None:
        """CLIContext accepts no_color parameter."""
        ctx = CLIContext(config=mock_config, no_color=True)
        assert ctx.no_color is True

    @pytest.mark.unit
    def test_init_creates_empty_state(self, mock_config: MagicMock) -> None:
        """CLIContext initializes with empty state dict."""
        ctx = CLIContext(config=mock_config)
        assert ctx._state == {}


class TestCLIContextOutputFormat:
    """Tests for output format detection methods."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "format_value,is_json,is_plain,is_table",
        [
            (OutputFormat.JSON, True, False, False),
            (OutputFormat.PLAIN, False, True, False),
            (OutputFormat.TABLE, False, False, True),
        ],
    )
    def test_output_format_detection(
        self,
        mock_config: MagicMock,
        format_value: OutputFormat,
        is_json: bool,
        is_plain: bool,
        is_table: bool,
    ) -> None:
        """Output format detection methods return correct values."""
        ctx = CLIContext(config=mock_config, output_format=format_value)
        assert ctx.is_json_output() == is_json
        assert ctx.is_plain_output() == is_plain
        assert ctx.is_table_output() == is_table

    @pytest.mark.unit
    def test_is_json_output_returns_bool(self, mock_config: MagicMock) -> None:
        """is_json_output() returns boolean."""
        ctx = CLIContext(config=mock_config, output_format=OutputFormat.JSON)
        result = ctx.is_json_output()
        assert isinstance(result, bool)
        assert result is True

    @pytest.mark.unit
    def test_is_plain_output_returns_bool(self, mock_config: MagicMock) -> None:
        """is_plain_output() returns boolean."""
        ctx = CLIContext(config=mock_config, output_format=OutputFormat.PLAIN)
        result = ctx.is_plain_output()
        assert isinstance(result, bool)
        assert result is True

    @pytest.mark.unit
    def test_is_table_output_returns_bool(self, mock_config: MagicMock) -> None:
        """is_table_output() returns boolean."""
        ctx = CLIContext(config=mock_config, output_format=OutputFormat.TABLE)
        result = ctx.is_table_output()
        assert isinstance(result, bool)
        assert result is True


class TestCLIContextState:
    """Tests for CLIContext state management."""

    @pytest.mark.unit
    def test_set_state_stores_value(self, mock_config: MagicMock) -> None:
        """set_state() stores value in state dict."""
        ctx = CLIContext(config=mock_config)
        ctx.set_state("key", "value")
        assert ctx._state["key"] == "value"

    @pytest.mark.unit
    def test_get_state_retrieves_value(self, mock_config: MagicMock) -> None:
        """get_state() retrieves stored value."""
        ctx = CLIContext(config=mock_config)
        ctx.set_state("test_key", "test_value")
        result = ctx.get_state("test_key")
        assert result == "test_value"

    @pytest.mark.unit
    def test_get_state_returns_default_for_missing_key(self, mock_config: MagicMock) -> None:
        """get_state() returns default for missing key."""
        ctx = CLIContext(config=mock_config)
        result = ctx.get_state("missing_key", default="default_value")
        assert result == "default_value"

    @pytest.mark.unit
    def test_get_state_returns_none_without_default(self, mock_config: MagicMock) -> None:
        """get_state() returns None when no default provided."""
        ctx = CLIContext(config=mock_config)
        result = ctx.get_state("missing_key")
        assert result is None

    @pytest.mark.unit
    def test_state_can_store_complex_values(self, mock_config: MagicMock) -> None:
        """State can store complex types like dicts and lists."""
        ctx = CLIContext(config=mock_config)
        ctx.set_state("sandbox_ids", ["sb_001", "sb_002"])
        ctx.set_state("metadata", {"name": "test", "count": 42})

        assert ctx.get_state("sandbox_ids") == ["sb_001", "sb_002"]
        assert ctx.get_state("metadata") == {"name": "test", "count": 42}

    @pytest.mark.unit
    def test_state_overwrites_existing_value(self, mock_config: MagicMock) -> None:
        """set_state() overwrites existing value for same key."""
        ctx = CLIContext(config=mock_config)
        ctx.set_state("key", "original")
        ctx.set_state("key", "updated")
        assert ctx.get_state("key") == "updated"


class TestCLIContextIntegration:
    """Integration tests for CLIContext behavior."""

    @pytest.mark.unit
    def test_context_loads_config_lazily(self, temp_hopx_dir: Any) -> None:
        """CLIContext loads config when not provided."""
        ctx = CLIContext()
        # Config should be loaded from defaults
        assert ctx.config is not None
        assert ctx.config.base_url == "https://api.hopx.dev"

    @pytest.mark.unit
    def test_context_respects_config_output_format(self, temp_hopx_dir: Any) -> None:
        """CLIContext uses output format from config."""
        from hopx_cli.core.config import CLIConfig

        config = CLIConfig(output_format="json")
        ctx = CLIContext(config=config)
        assert ctx.output_format == OutputFormat.JSON

    @pytest.mark.unit
    def test_explicit_format_overrides_config(self, temp_hopx_dir: Any) -> None:
        """Explicit output_format parameter overrides config."""
        from hopx_cli.core.config import CLIConfig

        config = CLIConfig(output_format="json")
        ctx = CLIContext(config=config, output_format=OutputFormat.PLAIN)
        assert ctx.output_format == OutputFormat.PLAIN
