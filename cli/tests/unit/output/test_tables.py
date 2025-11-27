"""Tests for table builders.

Tests cover:
- Generic build_table function
- Specialized table builders (Sandbox, Template, File, Process, Env)
- Value extraction from models, dicts, objects
- Formatter functions (status, time_ago, size, bool, file_type)
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel
from rich.table import Table

from hopx_cli.output.tables import (
    NULL_DISPLAY,
    EnvTable,
    FileTable,
    ProcessTable,
    SandboxTable,
    TemplateTable,
    _extract_value,
    _format_bool,
    _format_file_type,
    _format_size,
    _format_status,
    _format_time_ago,
    _format_value,
    build_table,
)


class TestBuildTable:
    """Tests for build_table function."""

    @pytest.mark.unit
    def test_creates_table_with_columns(self) -> None:
        """Creates table with specified columns."""
        columns = [
            {"name": "ID", "field": "id"},
            {"name": "Name", "field": "name"},
        ]
        data = [{"id": "1", "name": "test"}]

        table = build_table(data, columns)
        assert isinstance(table, Table)

    @pytest.mark.unit
    def test_table_has_title(self) -> None:
        """Table can have a title."""
        columns = [{"name": "ID", "field": "id"}]
        data = [{"id": "1"}]

        table = build_table(data, columns, title="Test Table")
        assert table.title == "Test Table"

    @pytest.mark.unit
    def test_handles_single_item(self) -> None:
        """Handles single item (not list) as data."""
        columns = [{"name": "ID", "field": "id"}]
        data = {"id": "single"}

        table = build_table(data, columns)
        assert table.row_count == 1

    @pytest.mark.unit
    def test_handles_empty_list(self) -> None:
        """Handles empty data list."""
        columns = [{"name": "ID", "field": "id"}]
        data: list[dict[str, Any]] = []

        table = build_table(data, columns)
        assert table.row_count == 0

    @pytest.mark.unit
    def test_column_alignment(self) -> None:
        """Respects column alignment settings."""
        columns = [
            {"name": "Left", "field": "left", "align": "left"},
            {"name": "Center", "field": "center", "align": "center"},
            {"name": "Right", "field": "right", "align": "right"},
        ]
        data = [{"left": "L", "center": "C", "right": "R"}]

        table = build_table(data, columns)
        assert table.columns[0].justify == "left"
        assert table.columns[1].justify == "center"
        assert table.columns[2].justify == "right"

    @pytest.mark.unit
    def test_column_style(self) -> None:
        """Applies column style."""
        columns = [
            {"name": "Styled", "field": "val", "style": "bold cyan"},
        ]
        data = [{"val": "test"}]

        table = build_table(data, columns)
        assert table.columns[0].style == "bold cyan"

    @pytest.mark.unit
    def test_applies_formatter(self) -> None:
        """Applies formatter to values."""
        columns = [
            {"name": "Status", "field": "status", "formatter": "status"},
        ]
        data = [{"status": "running"}]

        table = build_table(data, columns)
        # Table is built with formatter applied
        assert table.row_count == 1


class TestSandboxTable:
    """Tests for SandboxTable builder."""

    @pytest.mark.unit
    def test_builds_sandbox_table(self) -> None:
        """Builds table with sandbox columns."""
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

        table = SandboxTable.build(data)
        assert isinstance(table, Table)
        assert table.title == "Sandboxes"

    @pytest.mark.unit
    def test_custom_title(self) -> None:
        """Supports custom title."""
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

        table = SandboxTable.build(data, title="My Sandboxes")
        assert table.title == "My Sandboxes"

    @pytest.mark.unit
    def test_single_sandbox(self) -> None:
        """Builds table for single sandbox (not list)."""
        data = {
            "sandbox_id": "sb_456",
            "template_name": "nodejs",
            "status": "paused",
            "region": "eu-west-1",
            "created_at": None,
            "expires_at": None,
        }

        table = SandboxTable.build(data)
        assert table.row_count == 1


class TestTemplateTable:
    """Tests for TemplateTable builder."""

    @pytest.mark.unit
    def test_builds_template_table(self) -> None:
        """Builds table with template columns."""
        data = [
            {
                "name": "python",
                "display_name": "Python 3.11",
                "status": "active",
                "language": "python",
                "category": "General",
                "is_public": True,
            }
        ]

        table = TemplateTable.build(data)
        assert isinstance(table, Table)
        assert table.title == "Templates"

    @pytest.mark.unit
    def test_custom_title(self) -> None:
        """Supports custom title."""
        data = [
            {
                "name": "python",
                "display_name": "Python",
                "status": "active",
                "language": "python",
                "category": "General",
                "is_public": True,
            }
        ]

        table = TemplateTable.build(data, title="Available Templates")
        assert table.title == "Available Templates"


class TestFileTable:
    """Tests for FileTable builder."""

    @pytest.mark.unit
    def test_builds_file_table(self) -> None:
        """Builds table with file columns."""
        data = [
            {
                "name": "test.py",
                "type": "file",
                "size": 1024,
                "modified_at": None,
                "mode": "0644",
            }
        ]

        table = FileTable.build(data)
        assert isinstance(table, Table)
        assert table.title == "Files"

    @pytest.mark.unit
    def test_directory_entry(self) -> None:
        """Handles directory entries."""
        data = [
            {
                "name": "src",
                "type": "directory",
                "size": None,
                "modified_at": None,
                "mode": "0755",
            }
        ]

        table = FileTable.build(data)
        assert table.row_count == 1


class TestProcessTable:
    """Tests for ProcessTable builder."""

    @pytest.mark.unit
    def test_builds_process_table(self) -> None:
        """Builds table with process columns."""
        data = [
            {
                "pid": 1234,
                "command": "python app.py",
                "status": "running",
                "cpu_percent": "5.2",
                "memory_percent": "2.1",
                "started_at": None,
            }
        ]

        table = ProcessTable.build(data)
        assert isinstance(table, Table)
        assert table.title == "Processes"


class TestEnvTable:
    """Tests for EnvTable builder."""

    @pytest.mark.unit
    def test_builds_from_dict(self) -> None:
        """Builds table from environment dict."""
        data = {
            "PATH": "/usr/bin",
            "HOME": "/home/user",
        }

        table = EnvTable.build(data)
        assert isinstance(table, Table)
        assert table.row_count == 2
        assert table.title == "Environment Variables"

    @pytest.mark.unit
    def test_builds_from_list(self) -> None:
        """Builds table from list of dicts."""
        data = [
            {"name": "PATH", "value": "/usr/bin"},
            {"name": "HOME", "value": "/home/user"},
        ]

        table = EnvTable.build(data)
        assert table.row_count == 2

    @pytest.mark.unit
    def test_custom_title(self) -> None:
        """Supports custom title."""
        data = {"KEY": "value"}

        table = EnvTable.build(data, title="Environment")
        assert table.title == "Environment"


class TestExtractValue:
    """Tests for _extract_value helper."""

    @pytest.mark.unit
    def test_extracts_from_dict(self) -> None:
        """Extracts value from dictionary."""
        obj = {"name": "test", "id": 123}
        assert _extract_value(obj, "name") == "test"
        assert _extract_value(obj, "id") == 123

    @pytest.mark.unit
    def test_extracts_from_pydantic_model(self) -> None:
        """Extracts value from Pydantic model."""

        class TestModel(BaseModel):
            name: str
            count: int

        obj = TestModel(name="model", count=42)
        assert _extract_value(obj, "name") == "model"
        assert _extract_value(obj, "count") == 42

    @pytest.mark.unit
    def test_extracts_from_object(self) -> None:
        """Extracts value from generic object."""
        obj = MagicMock()
        obj.name = "mock"
        obj.value = 100

        assert _extract_value(obj, "name") == "mock"
        assert _extract_value(obj, "value") == 100

    @pytest.mark.unit
    def test_returns_none_for_missing_field(self) -> None:
        """Returns None for missing field."""
        obj = {"name": "test"}
        assert _extract_value(obj, "missing") is None

        obj2 = MagicMock(spec=[])
        assert _extract_value(obj2, "missing") is None


class TestFormatValue:
    """Tests for _format_value helper."""

    @pytest.mark.unit
    def test_formats_none_as_null_display(self) -> None:
        """None values show null display."""
        assert _format_value(None) == NULL_DISPLAY

    @pytest.mark.unit
    def test_formats_string_without_formatter(self) -> None:
        """Strings pass through without formatter."""
        assert _format_value("test") == "test"

    @pytest.mark.unit
    def test_formats_number_as_string(self) -> None:
        """Numbers convert to string."""
        assert _format_value(123) == "123"

    @pytest.mark.unit
    def test_applies_status_formatter(self) -> None:
        """Applies status formatter."""
        result = _format_value("running", "status")
        assert "running" in result
        assert "green" in result

    @pytest.mark.unit
    def test_applies_size_formatter(self) -> None:
        """Applies size formatter."""
        result = _format_value(1024, "size")
        assert "KB" in result

    @pytest.mark.unit
    def test_applies_bool_formatter(self) -> None:
        """Applies bool formatter."""
        result = _format_value(True, "bool")
        assert "Yes" in result


class TestFormatStatus:
    """Tests for _format_status formatter."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "status,expected_color",
        [
            ("running", "green"),
            ("active", "green"),
            ("ready", "green"),
            ("success", "green"),
            ("paused", "yellow"),
            ("pending", "yellow"),
            ("building", "yellow"),
            ("publishing", "yellow"),
            ("error", "red"),
            ("failed", "red"),
            ("stopped", "red"),
            ("killed", "red"),
        ],
    )
    def test_status_colors(self, status: str, expected_color: str) -> None:
        """Each status maps to correct color."""
        result = _format_status(status)
        assert expected_color in result
        assert status in result

    @pytest.mark.unit
    def test_unknown_status_passes_through(self) -> None:
        """Unknown status passes through as string."""
        result = _format_status("custom_status")
        assert result == "custom_status"

    @pytest.mark.unit
    def test_case_insensitive(self) -> None:
        """Status matching is case insensitive."""
        assert "green" in _format_status("RUNNING")
        assert "green" in _format_status("Running")


class TestFormatTimeAgo:
    """Tests for _format_time_ago formatter."""

    @pytest.mark.unit
    def test_formats_none(self) -> None:
        """None returns null display."""
        assert _format_time_ago(None) == NULL_DISPLAY

    @pytest.mark.unit
    def test_formats_seconds_ago(self) -> None:
        """Formats recent time as seconds."""
        now = datetime.now(UTC)
        dt = now - timedelta(seconds=30)
        result = _format_time_ago(dt)
        assert "30s ago" in result

    @pytest.mark.unit
    def test_formats_minutes_ago(self) -> None:
        """Formats time as minutes."""
        now = datetime.now(UTC)
        dt = now - timedelta(minutes=5)
        result = _format_time_ago(dt)
        assert "5m ago" in result

    @pytest.mark.unit
    def test_formats_hours_ago(self) -> None:
        """Formats time as hours and minutes."""
        now = datetime.now(UTC)
        dt = now - timedelta(hours=2, minutes=15)
        result = _format_time_ago(dt)
        assert "2h" in result
        assert "ago" in result

    @pytest.mark.unit
    def test_formats_days_ago(self) -> None:
        """Formats time as days."""
        now = datetime.now(UTC)
        dt = now - timedelta(days=3)
        result = _format_time_ago(dt)
        assert "3d" in result
        assert "ago" in result

    @pytest.mark.unit
    def test_formats_weeks_ago(self) -> None:
        """Formats time as weeks."""
        now = datetime.now(UTC)
        dt = now - timedelta(weeks=2)
        result = _format_time_ago(dt)
        assert "2w ago" in result

    @pytest.mark.unit
    def test_formats_future_time(self) -> None:
        """Formats future time with 'from now'."""
        now = datetime.now(UTC)
        dt = now + timedelta(hours=1)
        result = _format_time_ago(dt)
        assert "from now" in result

    @pytest.mark.unit
    def test_parses_iso_string(self) -> None:
        """Parses ISO format string."""
        now = datetime.now(UTC)
        dt = now - timedelta(minutes=10)
        iso_str = dt.isoformat()
        result = _format_time_ago(iso_str)
        assert "10m ago" in result

    @pytest.mark.unit
    def test_handles_invalid_string(self) -> None:
        """Invalid string passes through."""
        result = _format_time_ago("not a date")
        assert result == "not a date"

    @pytest.mark.unit
    def test_handles_non_datetime(self) -> None:
        """Non-datetime objects convert to string."""
        result = _format_time_ago(12345)
        assert result == "12345"


class TestFormatSize:
    """Tests for _format_size formatter."""

    @pytest.mark.unit
    def test_formats_none(self) -> None:
        """None returns null display."""
        assert _format_size(None) == NULL_DISPLAY

    @pytest.mark.unit
    def test_formats_bytes(self) -> None:
        """Small values show as bytes."""
        assert _format_size(500) == "500 B"

    @pytest.mark.unit
    def test_formats_kilobytes(self) -> None:
        """KB range values."""
        result = _format_size(1024)
        assert "1.0 KB" in result

        result = _format_size(2560)
        assert "2.5 KB" in result

    @pytest.mark.unit
    def test_formats_megabytes(self) -> None:
        """MB range values."""
        result = _format_size(1024 * 1024)
        assert "1.0 MB" in result

        result = _format_size(1024 * 1024 * 5)
        assert "5.0 MB" in result

    @pytest.mark.unit
    def test_formats_gigabytes(self) -> None:
        """GB range values."""
        result = _format_size(1024 * 1024 * 1024)
        assert "1.00 GB" in result

    @pytest.mark.unit
    def test_handles_invalid_value(self) -> None:
        """Invalid value passes through."""
        result = _format_size("not a number")
        assert result == "not a number"

    @pytest.mark.unit
    def test_handles_string_number(self) -> None:
        """String numbers are parsed."""
        result = _format_size("1024")
        assert "1.0 KB" in result


class TestFormatBool:
    """Tests for _format_bool formatter."""

    @pytest.mark.unit
    def test_formats_none(self) -> None:
        """None returns null display."""
        assert _format_bool(None) == NULL_DISPLAY

    @pytest.mark.unit
    def test_formats_true(self) -> None:
        """True shows as Yes with green."""
        result = _format_bool(True)
        assert "Yes" in result
        assert "green" in result

    @pytest.mark.unit
    def test_formats_false(self) -> None:
        """False shows as No dimmed."""
        result = _format_bool(False)
        assert "No" in result
        assert "dim" in result

    @pytest.mark.unit
    def test_formats_string_true(self) -> None:
        """String 'true' shows as Yes."""
        result = _format_bool("true")
        assert "Yes" in result

        result = _format_bool("TRUE")
        assert "Yes" in result

    @pytest.mark.unit
    def test_formats_string_false(self) -> None:
        """String 'false' shows as No."""
        result = _format_bool("false")
        assert "No" in result

    @pytest.mark.unit
    def test_other_values_pass_through(self) -> None:
        """Other values pass through as string."""
        result = _format_bool("maybe")
        assert result == "maybe"


class TestFormatFileType:
    """Tests for _format_file_type formatter."""

    @pytest.mark.unit
    def test_formats_none(self) -> None:
        """None returns null display."""
        assert _format_file_type(None) == NULL_DISPLAY

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "file_type",
        ["directory", "dir", "folder"],
    )
    def test_formats_directory(self, file_type: str) -> None:
        """Directory types show as DIR."""
        result = _format_file_type(file_type)
        assert "DIR" in result
        assert "blue" in result

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "file_type",
        ["file", "regular"],
    )
    def test_formats_file(self, file_type: str) -> None:
        """File types show as FILE."""
        result = _format_file_type(file_type)
        assert "FILE" in result

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "file_type",
        ["symlink", "link"],
    )
    def test_formats_symlink(self, file_type: str) -> None:
        """Symlink types show as LINK."""
        result = _format_file_type(file_type)
        assert "LINK" in result
        assert "cyan" in result

    @pytest.mark.unit
    def test_unknown_type_passes_through(self) -> None:
        """Unknown type passes through as string."""
        result = _format_file_type("socket")
        assert result == "socket"
