"""Tests for output formatters.

Tests cover:
- JSON formatter with various data types
- Plain text formatter for scripting
- Main format_output dispatcher
- format_timestamp utility
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from hopx_cli.core.context import OutputFormat
from hopx_cli.output.formatters import format_output, format_timestamp
from hopx_cli.output.json_formatter import _json_serializer, format_json
from hopx_cli.output.plain_formatter import (
    _extract_field,
    _format_dict,
    _format_list,
    _format_model,
    _get_primary_id_field,
    format_plain,
)


# Test models
class SampleModel(BaseModel):
    sandbox_id: str
    status: str
    name: str | None = None


class NamedModel(BaseModel):
    name: str
    value: int


class TestFormatJson:
    """Tests for format_json function."""

    @pytest.mark.unit
    def test_formats_dict(self) -> None:
        """Formats simple dict to JSON."""
        data = {"key": "value", "count": 42}
        result = format_json(data)
        parsed = json.loads(result)
        assert parsed["key"] == "value"
        assert parsed["count"] == 42

    @pytest.mark.unit
    def test_formats_list(self) -> None:
        """Formats list to JSON array."""
        data = [1, 2, 3, "four"]
        result = format_json(data)
        parsed = json.loads(result)
        assert parsed == [1, 2, 3, "four"]

    @pytest.mark.unit
    def test_formats_pydantic_model(self) -> None:
        """Formats Pydantic model to JSON."""
        model = SampleModel(sandbox_id="sb_123", status="running")
        result = format_json(model)
        parsed = json.loads(result)
        assert parsed["sandbox_id"] == "sb_123"
        assert parsed["status"] == "running"

    @pytest.mark.unit
    def test_formats_list_of_models(self) -> None:
        """Formats list of Pydantic models."""
        models = [
            SampleModel(sandbox_id="sb_1", status="running"),
            SampleModel(sandbox_id="sb_2", status="paused"),
        ]
        result = format_json(models)
        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["sandbox_id"] == "sb_1"
        assert parsed[1]["sandbox_id"] == "sb_2"

    @pytest.mark.unit
    def test_compact_mode(self) -> None:
        """Compact mode outputs single line."""
        data = {"key": "value"}
        result = format_json(data, compact=True)
        assert "\n" not in result

    @pytest.mark.unit
    def test_custom_indent(self) -> None:
        """Custom indent level."""
        data = {"key": "value"}
        result = format_json(data, indent=4)
        # Should have 4 spaces of indent
        assert "    " in result


class TestJsonSerializer:
    """Tests for _json_serializer helper."""

    @pytest.mark.unit
    def test_serializes_pydantic_model(self) -> None:
        """Pydantic model converts to dict."""
        model = SampleModel(sandbox_id="sb_123", status="running")
        result = _json_serializer(model)
        assert result["sandbox_id"] == "sb_123"

    @pytest.mark.unit
    def test_serializes_datetime(self) -> None:
        """Datetime converts to ISO format."""
        dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
        result = _json_serializer(dt)
        assert "2024-01-15" in result
        assert "10:30:00" in result

    @pytest.mark.unit
    def test_serializes_bytes(self) -> None:
        """Bytes convert to base64."""
        data = b"hello world"
        result = _json_serializer(data)
        assert result == "aGVsbG8gd29ybGQ="

    @pytest.mark.unit
    def test_serializes_set(self) -> None:
        """Set converts to list."""
        data = {1, 2, 3}
        result = _json_serializer(data)
        assert sorted(result) == [1, 2, 3]

    @pytest.mark.unit
    def test_serializes_object_with_dict(self) -> None:
        """Object with __dict__ uses that."""

        class CustomObj:
            def __init__(self) -> None:
                self.name = "test"
                self.value = 42

        obj = CustomObj()
        result = _json_serializer(obj)
        assert result["name"] == "test"
        assert result["value"] == 42

    @pytest.mark.unit
    def test_raises_for_unserializable(self) -> None:
        """Raises TypeError for unserializable objects."""

        class Unserializable:
            __slots__ = ()

        obj = Unserializable()
        with pytest.raises(TypeError, match="not JSON serializable"):
            _json_serializer(obj)


class TestFormatPlain:
    """Tests for format_plain function."""

    @pytest.mark.unit
    def test_formats_none(self) -> None:
        """None returns empty string."""
        assert format_plain(None) == ""

    @pytest.mark.unit
    def test_formats_empty_list(self) -> None:
        """Empty list returns empty string."""
        assert format_plain([]) == ""

    @pytest.mark.unit
    def test_formats_empty_dict(self) -> None:
        """Empty dict returns empty string."""
        assert format_plain({}) == ""

    @pytest.mark.unit
    def test_formats_string_list(self) -> None:
        """List of strings joins with newlines."""
        data = ["one", "two", "three"]
        result = format_plain(data)
        assert result == "one\ntwo\nthree"

    @pytest.mark.unit
    def test_formats_dict(self) -> None:
        """Dict formats as key: value."""
        data = {"name": "test", "status": "running"}
        result = format_plain(data)
        assert "name: test" in result
        assert "status: running" in result

    @pytest.mark.unit
    def test_formats_pydantic_model(self) -> None:
        """Pydantic model formats as key: value."""
        model = SampleModel(sandbox_id="sb_123", status="running")
        result = format_plain(model)
        assert "sandbox_id: sb_123" in result
        assert "status: running" in result

    @pytest.mark.unit
    def test_formats_model_with_field(self) -> None:
        """Extracts specific field from model."""
        model = SampleModel(sandbox_id="sb_123", status="running")
        result = format_plain(model, field="sandbox_id")
        assert result == "sb_123"

    @pytest.mark.unit
    def test_formats_dict_with_field(self) -> None:
        """Extracts specific field from dict."""
        data = {"id": "123", "name": "test"}
        result = format_plain(data, field="id")
        assert result == "123"

    @pytest.mark.unit
    def test_formats_primitive(self) -> None:
        """Primitive types convert to string."""
        assert format_plain(42) == "42"
        assert format_plain("hello") == "hello"
        assert format_plain(True) == "True"


class TestFormatList:
    """Tests for _format_list helper."""

    @pytest.mark.unit
    def test_empty_list(self) -> None:
        """Empty list returns empty string."""
        assert _format_list([]) == ""

    @pytest.mark.unit
    def test_extracts_field_from_models(self) -> None:
        """Extracts specified field from list of models."""
        models = [
            SampleModel(sandbox_id="sb_1", status="running"),
            SampleModel(sandbox_id="sb_2", status="paused"),
        ]
        result = _format_list(models, field="sandbox_id")
        assert result == "sb_1\nsb_2"

    @pytest.mark.unit
    def test_extracts_primary_id_from_models(self) -> None:
        """Extracts primary ID field without explicit field."""
        models = [
            SampleModel(sandbox_id="sb_1", status="running"),
            SampleModel(sandbox_id="sb_2", status="paused"),
        ]
        result = _format_list(models)
        assert "sb_1" in result
        assert "sb_2" in result

    @pytest.mark.unit
    def test_extracts_id_from_dicts(self) -> None:
        """Extracts id field from list of dicts."""
        dicts = [
            {"id": "1", "name": "first"},
            {"id": "2", "name": "second"},
        ]
        result = _format_list(dicts)
        assert "1" in result
        assert "2" in result

    @pytest.mark.unit
    def test_handles_primitives(self) -> None:
        """Handles list of primitives."""
        items = [1, 2, 3]
        result = _format_list(items)
        assert result == "1\n2\n3"


class TestFormatModel:
    """Tests for _format_model helper."""

    @pytest.mark.unit
    def test_extracts_field(self) -> None:
        """Extracts specific field."""
        model = SampleModel(sandbox_id="sb_123", status="running")
        result = _format_model(model, field="status")
        assert result == "running"

    @pytest.mark.unit
    def test_returns_empty_for_missing_field(self) -> None:
        """Returns empty for missing field."""
        model = SampleModel(sandbox_id="sb_123", status="running")
        result = _format_model(model, field="nonexistent")
        assert result == ""

    @pytest.mark.unit
    def test_formats_all_fields(self) -> None:
        """Formats all fields without specific field."""
        model = SampleModel(sandbox_id="sb_123", status="running")
        result = _format_model(model)
        assert "sandbox_id: sb_123" in result
        assert "status: running" in result


class TestFormatDict:
    """Tests for _format_dict helper."""

    @pytest.mark.unit
    def test_extracts_field(self) -> None:
        """Extracts specific field."""
        data = {"id": "123", "name": "test"}
        result = _format_dict(data, field="id")
        assert result == "123"

    @pytest.mark.unit
    def test_returns_empty_for_missing_field(self) -> None:
        """Returns empty for missing field."""
        data = {"id": "123"}
        result = _format_dict(data, field="missing")
        assert result == ""

    @pytest.mark.unit
    def test_skips_none_values(self) -> None:
        """Skips None values in output."""
        data = {"id": "123", "name": None}
        result = _format_dict(data)
        assert "id: 123" in result
        assert "name" not in result

    @pytest.mark.unit
    def test_skips_complex_nested(self) -> None:
        """Skips nested dicts and lists."""
        data = {"id": "123", "nested": {"key": "val"}, "items": [1, 2]}
        result = _format_dict(data)
        assert "id: 123" in result
        assert "nested" not in result
        assert "items" not in result


class TestExtractField:
    """Tests for _extract_field helper."""

    @pytest.mark.unit
    def test_extracts_from_model(self) -> None:
        """Extracts from Pydantic model."""
        model = SampleModel(sandbox_id="sb_123", status="running")
        assert _extract_field(model, "sandbox_id") == "sb_123"

    @pytest.mark.unit
    def test_extracts_from_dict(self) -> None:
        """Extracts from dict."""
        data = {"key": "value"}
        assert _extract_field(data, "key") == "value"

    @pytest.mark.unit
    def test_extracts_from_object(self) -> None:
        """Extracts from generic object."""
        obj = MagicMock()
        obj.field = "test"
        assert _extract_field(obj, "field") == "test"

    @pytest.mark.unit
    def test_returns_none_for_missing(self) -> None:
        """Returns None for missing field."""
        data = {"key": "value"}
        assert _extract_field(data, "missing") is None


class TestGetPrimaryIdField:
    """Tests for _get_primary_id_field helper."""

    @pytest.mark.unit
    def test_finds_sandbox_id(self) -> None:
        """Finds sandbox_id as primary."""
        model = SampleModel(sandbox_id="sb_123", status="running")
        assert _get_primary_id_field(model) == "sandbox_id"

    @pytest.mark.unit
    def test_finds_name(self) -> None:
        """Finds name field."""
        model = NamedModel(name="test", value=42)
        assert _get_primary_id_field(model) == "name"

    @pytest.mark.unit
    def test_returns_none_for_no_id(self) -> None:
        """Returns None when no ID field exists."""

        class NoIdModel(BaseModel):
            value: int
            data: str

        model = NoIdModel(value=42, data="test")
        assert _get_primary_id_field(model) is None


class TestFormatTimestamp:
    """Tests for format_timestamp utility."""

    @pytest.mark.unit
    def test_formats_none(self) -> None:
        """None returns null display."""
        from hopx_cli.output.tables import NULL_DISPLAY

        result = format_timestamp(None)
        assert result == NULL_DISPLAY

    @pytest.mark.unit
    def test_formats_datetime(self) -> None:
        """Formats datetime with ISO and relative."""
        dt = datetime.now(UTC) - timedelta(hours=2)
        result = format_timestamp(dt)
        # Should have ISO format
        assert "-" in result  # date separator
        assert ":" in result  # time separator
        # Should have relative time
        assert "ago" in result

    @pytest.mark.unit
    def test_without_relative(self) -> None:
        """Can disable relative time."""
        dt = datetime.now(UTC)
        result = format_timestamp(dt, include_relative=False)
        assert "ago" not in result

    @pytest.mark.unit
    def test_parses_iso_string(self) -> None:
        """Parses ISO format string."""
        iso_str = "2024-01-15T10:30:00Z"
        result = format_timestamp(iso_str, include_relative=False)
        assert "2024-01-15" in result
        assert "10:30:00" in result

    @pytest.mark.unit
    def test_handles_invalid_string(self) -> None:
        """Invalid string passes through."""
        result = format_timestamp("not a date")
        assert result == "not a date"

    @pytest.mark.unit
    def test_handles_non_datetime(self) -> None:
        """Non-datetime objects convert to string."""
        result = format_timestamp(12345)
        assert result == "12345"


class TestFormatOutput:
    """Tests for format_output dispatcher."""

    @pytest.mark.unit
    def test_dispatches_to_json(self) -> None:
        """JSON format uses json_formatter."""
        with patch("hopx_cli.output.formatters.Console") as MockConsole:
            mock_console = MagicMock()
            MockConsole.return_value = mock_console

            data = {"key": "value"}
            format_output(data, OutputFormat.JSON)

            mock_console.print.assert_called_once()
            call_arg = mock_console.print.call_args[0][0]
            assert '"key"' in call_arg
            assert '"value"' in call_arg

    @pytest.mark.unit
    def test_dispatches_to_plain(self) -> None:
        """PLAIN format uses plain_formatter."""
        with patch("hopx_cli.output.formatters.Console") as MockConsole:
            mock_console = MagicMock()
            MockConsole.return_value = mock_console

            data = {"name": "test", "status": "running"}
            format_output(data, OutputFormat.PLAIN)

            mock_console.print.assert_called_once()

    @pytest.mark.unit
    def test_dispatches_to_table(self) -> None:
        """TABLE format builds rich table."""
        with patch("hopx_cli.output.formatters.Console") as MockConsole:
            mock_console = MagicMock()
            MockConsole.return_value = mock_console

            data = [
                {
                    "sandbox_id": "sb_123",
                    "template_name": "python",
                    "status": "running",
                    "region": "us-east-1",
                    "created_at": None,
                    "expires_at": None,
                }
            ]
            format_output(data, OutputFormat.TABLE, {"table_type": "sandbox"})

            mock_console.print.assert_called_once()

    @pytest.mark.unit
    def test_uses_provided_console(self) -> None:
        """Uses provided console instance."""
        mock_console = MagicMock()

        data = {"key": "value"}
        format_output(data, OutputFormat.JSON, console=mock_console)

        mock_console.print.assert_called_once()

    @pytest.mark.unit
    def test_handles_empty_list(self) -> None:
        """Handles empty list with message."""
        mock_console = MagicMock()

        format_output([], OutputFormat.TABLE, {"table_type": "sandbox"}, console=mock_console)

        mock_console.print.assert_called_once()
        call_arg = str(mock_console.print.call_args)
        assert "No" in call_arg or "found" in call_arg

    @pytest.mark.unit
    def test_handles_empty_data(self) -> None:
        """Handles empty/None data."""
        mock_console = MagicMock()

        format_output(None, OutputFormat.TABLE, console=mock_console)

        mock_console.print.assert_called_once()

    @pytest.mark.unit
    def test_table_with_custom_columns(self) -> None:
        """TABLE format with custom columns."""
        mock_console = MagicMock()

        columns = [
            {"name": "ID", "field": "id"},
            {"name": "Value", "field": "value"},
        ]
        data = [{"id": "1", "value": "test"}]
        format_output(data, OutputFormat.TABLE, {"columns": columns}, console=mock_console)

        mock_console.print.assert_called_once()

    @pytest.mark.unit
    def test_unknown_format_falls_back_to_json(self) -> None:
        """Unknown format falls back to JSON."""
        mock_console = MagicMock()

        # Create a fake output format
        class FakeFormat:
            pass

        data = {"key": "value"}
        format_output(data, FakeFormat(), console=mock_console)  # type: ignore

        mock_console.print.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "table_type",
        ["sandbox", "template", "file", "process", "env"],
    )
    def test_all_table_types(self, table_type: str) -> None:
        """All table types dispatch correctly."""
        mock_console = MagicMock()

        # Build appropriate data for each type
        data_map = {
            "sandbox": {
                "sandbox_id": "sb_123",
                "template_name": "python",
                "status": "running",
                "region": "us-east-1",
                "created_at": None,
                "expires_at": None,
            },
            "template": {
                "name": "python",
                "display_name": "Python",
                "status": "active",
                "language": "python",
                "category": "General",
                "is_public": True,
            },
            "file": {
                "name": "test.py",
                "type": "file",
                "size": 1024,
                "modified_at": None,
                "mode": "0644",
            },
            "process": {
                "pid": 123,
                "command": "python",
                "status": "running",
                "cpu_percent": "1.0",
                "memory_percent": "2.0",
                "started_at": None,
            },
            "env": {"PATH": "/usr/bin", "HOME": "/home/user"},
        }

        data = data_map[table_type]
        format_output(data, OutputFormat.TABLE, {"table_type": table_type}, console=mock_console)

        mock_console.print.assert_called_once()
