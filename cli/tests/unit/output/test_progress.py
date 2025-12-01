"""Tests for progress indicators and live output.

Tests cover:
- Spinner context manager
- ProgressBar context manager
- StatusPanel display
- LiveOutput streaming
"""

from __future__ import annotations

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console


class TestSpinner:
    """Tests for Spinner class."""

    @pytest.mark.unit
    def test_init_stores_message(self) -> None:
        """Initializes with message."""
        from hopx_cli.output.progress import Spinner

        spinner = Spinner("Loading...")
        assert spinner.message == "Loading..."

    @pytest.mark.unit
    def test_init_default_spinner_name(self) -> None:
        """Uses 'dots' spinner by default."""
        from hopx_cli.output.progress import Spinner

        spinner = Spinner("Loading...")
        assert spinner.spinner_name == "dots"

    @pytest.mark.unit
    def test_init_custom_spinner_name(self) -> None:
        """Accepts custom spinner name."""
        from hopx_cli.output.progress import Spinner

        spinner = Spinner("Loading...", spinner_name="line")
        assert spinner.spinner_name == "line"

    @pytest.mark.unit
    def test_context_manager_returns_self(self) -> None:
        """Context manager returns spinner instance."""
        from hopx_cli.output.progress import Spinner

        with patch("hopx_cli.output.progress.Live"):
            spinner = Spinner("Loading...")
            with spinner as s:
                assert s is spinner

    @pytest.mark.unit
    def test_start_respects_no_color(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Respects NO_COLOR environment variable."""
        from hopx_cli.output.progress import Spinner

        monkeypatch.setenv("NO_COLOR", "1")

        output = StringIO()
        console = Console(file=output, force_terminal=True)
        spinner = Spinner("Loading...", console=console)

        spinner.start()

        assert "Loading..." in output.getvalue()
        assert spinner._live is None

    @pytest.mark.unit
    def test_start_creates_live_display(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Creates Live display when NO_COLOR not set."""
        from hopx_cli.output.progress import Spinner

        monkeypatch.delenv("NO_COLOR", raising=False)

        with patch("hopx_cli.output.progress.Live") as mock_live:
            spinner = Spinner("Loading...")
            spinner.start()

            mock_live.assert_called_once()
            mock_live.return_value.start.assert_called_once()

    @pytest.mark.unit
    def test_stop_clears_live_display(self) -> None:
        """Stop clears live display."""
        from hopx_cli.output.progress import Spinner

        mock_live = MagicMock()
        with patch("hopx_cli.output.progress.Live", return_value=mock_live):
            spinner = Spinner("Loading...")
            spinner.start()
            spinner.stop()

            mock_live.stop.assert_called_once()
            assert spinner._live is None

    @pytest.mark.unit
    def test_stop_is_idempotent(self) -> None:
        """Stop can be called multiple times."""
        from hopx_cli.output.progress import Spinner

        spinner = Spinner("Loading...")
        spinner.stop()  # No-op when not started
        spinner.stop()  # Still no-op

    @pytest.mark.unit
    def test_update_changes_message(self) -> None:
        """Update changes spinner message."""
        from hopx_cli.output.progress import Spinner

        mock_spinner = MagicMock()
        with patch("hopx_cli.output.progress.Live"):
            with patch("hopx_cli.output.progress.RichSpinner", return_value=mock_spinner):
                spinner = Spinner("Loading...")
                spinner.start()
                spinner.update("Still loading...")

                assert spinner.message == "Still loading..."
                mock_spinner.update.assert_called_with(text="Still loading...")

    @pytest.mark.unit
    def test_success_stops_and_prints(self) -> None:
        """Success stops spinner and prints success message."""
        from hopx_cli.output.progress import Spinner

        output = StringIO()
        console = Console(file=output, force_terminal=True)

        with patch("hopx_cli.output.progress.Live"):
            spinner = Spinner("Loading...", console=console)
            spinner.start()
            spinner.success("Done!")

        assert "Done!" in output.getvalue()

    @pytest.mark.unit
    def test_error_stops_and_prints(self) -> None:
        """Error stops spinner and prints error message."""
        from hopx_cli.output.progress import Spinner

        output = StringIO()
        console = Console(file=output, force_terminal=True)

        with patch("hopx_cli.output.progress.Live"):
            spinner = Spinner("Loading...", console=console)
            spinner.start()
            spinner.error("Failed!")

        assert "Failed!" in output.getvalue()

    @pytest.mark.unit
    def test_warn_stops_and_prints(self) -> None:
        """Warn stops spinner and prints warning message."""
        from hopx_cli.output.progress import Spinner

        output = StringIO()
        console = Console(file=output, force_terminal=True)

        with patch("hopx_cli.output.progress.Live"):
            spinner = Spinner("Loading...", console=console)
            spinner.start()
            spinner.warn("Warning!")

        assert "Warning!" in output.getvalue()

    @pytest.mark.unit
    def test_context_manager_success_on_normal_exit(self) -> None:
        """Shows success on normal context exit."""
        from hopx_cli.output.progress import Spinner

        output = StringIO()
        console = Console(file=output, force_terminal=True)

        with patch("hopx_cli.output.progress.Live"):
            with Spinner("Loading...", console=console):
                pass

        # Should show the message as success (with checkmark)
        # Rich adds ANSI escape codes, so check for key parts
        result = output.getvalue()
        assert "Loading" in result

    @pytest.mark.unit
    def test_context_manager_error_on_exception(self) -> None:
        """Shows error on exception exit."""
        from hopx_cli.output.progress import Spinner

        output = StringIO()
        console = Console(file=output, force_terminal=True)

        with patch("hopx_cli.output.progress.Live"):
            try:
                with Spinner("Loading...", console=console):
                    raise ValueError("test error")
            except ValueError:
                pass

        assert "Failed" in output.getvalue()


class TestProgressBar:
    """Tests for ProgressBar class."""

    @pytest.mark.unit
    def test_init_with_description(self) -> None:
        """Initializes with description."""
        from hopx_cli.output.progress import ProgressBar

        bar = ProgressBar("Uploading")
        assert bar._description == "Uploading"

    @pytest.mark.unit
    def test_init_default_description(self) -> None:
        """Uses 'Processing' as default description."""
        from hopx_cli.output.progress import ProgressBar

        bar = ProgressBar()
        assert bar._description == "Processing"

    @pytest.mark.unit
    def test_context_manager_returns_self(self) -> None:
        """Context manager returns progress bar instance."""
        from hopx_cli.output.progress import ProgressBar

        with patch("hopx_cli.output.progress.Progress") as mock_progress_class:
            mock_progress = MagicMock()
            mock_progress_class.return_value = mock_progress
            mock_progress.add_task.return_value = 0

            bar = ProgressBar()
            with bar as b:
                assert b is bar

            mock_progress.start.assert_called_once()
            mock_progress.stop.assert_called_once()

    @pytest.mark.unit
    def test_add_task_returns_task_id(self) -> None:
        """Add task returns task ID."""
        from hopx_cli.output.progress import ProgressBar

        bar = ProgressBar()
        bar._progress = MagicMock()
        bar._progress.add_task.return_value = 42

        task_id = bar.add_task("Download", total=100)
        assert task_id == 42
        bar._progress.add_task.assert_called_with("Download", total=100)

    @pytest.mark.unit
    def test_update_forwards_to_progress(self) -> None:
        """Update forwards to internal progress."""
        from hopx_cli.output.progress import ProgressBar

        bar = ProgressBar()
        bar._progress = MagicMock()

        bar.update(task_id=1, advance=10)
        bar._progress.update.assert_called_with(1, advance=10)

    @pytest.mark.unit
    def test_advance_updates_main_task(self) -> None:
        """Advance updates main task progress."""
        from hopx_cli.output.progress import ProgressBar

        bar = ProgressBar(total=100)
        bar._progress = MagicMock()
        bar._main_task = 0

        bar.advance(5)
        bar._progress.update.assert_called_with(0, advance=5)

    @pytest.mark.unit
    def test_advance_no_op_without_main_task(self) -> None:
        """Advance is no-op when no main task."""
        from hopx_cli.output.progress import ProgressBar

        bar = ProgressBar()
        bar._progress = MagicMock()
        bar._main_task = None

        bar.advance(5)
        bar._progress.update.assert_not_called()


class TestStatusPanel:
    """Tests for StatusPanel class."""

    @pytest.mark.unit
    def test_init_with_title(self) -> None:
        """Initializes with title."""
        from hopx_cli.output.progress import StatusPanel

        panel = StatusPanel("Build Status")
        assert panel.title == "Build Status"

    @pytest.mark.unit
    def test_add_stores_items(self) -> None:
        """Add stores key-value pairs."""
        from hopx_cli.output.progress import StatusPanel

        panel = StatusPanel("Status")
        panel.add("Template", "my-app")
        panel.add("Status", "Building", style="yellow")

        assert len(panel._items) == 2
        assert panel._items[0] == ("Template", "my-app", None)
        assert panel._items[1] == ("Status", "Building", "yellow")

    @pytest.mark.unit
    def test_display_renders_panel(self) -> None:
        """Display renders panel with items."""
        from hopx_cli.output.progress import StatusPanel

        output = StringIO()
        console = Console(file=output, force_terminal=True)

        panel = StatusPanel("Build Status", console=console)
        panel.add("Template", "my-app")
        panel.add("Progress", "45%")
        panel.display()

        result = output.getvalue()
        assert "Template" in result
        assert "my-app" in result
        assert "45%" in result

    @pytest.mark.unit
    def test_display_empty_no_output(self) -> None:
        """Display with no items produces no output."""
        from hopx_cli.output.progress import StatusPanel

        output = StringIO()
        console = Console(file=output, force_terminal=True)

        panel = StatusPanel("Status", console=console)
        panel.display()

        assert output.getvalue() == ""


class TestLiveOutput:
    """Tests for LiveOutput class."""

    @pytest.mark.unit
    def test_init_with_title(self) -> None:
        """Initializes with title."""
        from hopx_cli.output.progress import LiveOutput

        live = LiveOutput(title="Build Logs")
        assert live.title == "Build Logs"

    @pytest.mark.unit
    def test_init_with_max_lines(self) -> None:
        """Initializes with max lines."""
        from hopx_cli.output.progress import LiveOutput

        live = LiveOutput(max_lines=100)
        assert live.max_lines == 100

    @pytest.mark.unit
    def test_context_manager_returns_self(self) -> None:
        """Context manager returns live output instance."""
        from hopx_cli.output.progress import LiveOutput

        with patch("hopx_cli.output.progress.Live"):
            live = LiveOutput()
            with live as live_instance:
                assert live_instance is live

    @pytest.mark.unit
    def test_append_adds_line(self) -> None:
        """Append adds line to output."""
        from hopx_cli.output.progress import LiveOutput

        live = LiveOutput()
        live._live = MagicMock()

        live.append("Line 1")
        live.append("Line 2")

        assert live._lines == ["Line 1", "Line 2"]

    @pytest.mark.unit
    def test_append_trims_to_max_lines(self) -> None:
        """Append trims lines to max."""
        from hopx_cli.output.progress import LiveOutput

        live = LiveOutput(max_lines=3)
        live._live = MagicMock()

        for i in range(5):
            live.append(f"Line {i}")

        assert len(live._lines) == 3
        assert live._lines == ["Line 2", "Line 3", "Line 4"]

    @pytest.mark.unit
    def test_clear_removes_lines(self) -> None:
        """Clear removes all lines."""
        from hopx_cli.output.progress import LiveOutput

        live = LiveOutput()
        live._live = MagicMock()
        live._lines = ["Line 1", "Line 2"]

        live.clear()

        assert live._lines == []

    @pytest.mark.unit
    def test_render_with_title_returns_panel(self) -> None:
        """Render with title returns Panel."""
        from rich.panel import Panel

        from hopx_cli.output.progress import LiveOutput

        live = LiveOutput(title="Output")
        live._lines = ["Test line"]

        result = live._render()
        assert isinstance(result, Panel)

    @pytest.mark.unit
    def test_render_without_title_returns_text(self) -> None:
        """Render without title returns Text."""
        from rich.text import Text

        from hopx_cli.output.progress import LiveOutput

        live = LiveOutput()
        live._lines = ["Test line"]

        result = live._render()
        assert isinstance(result, Text)

    @pytest.mark.unit
    def test_render_empty_shows_placeholder(self) -> None:
        """Render with no lines shows placeholder."""
        from hopx_cli.output.progress import LiveOutput

        live = LiveOutput(title="Output")
        result = live._render()

        # Panel content should contain placeholder
        assert "No output yet" in str(result.renderable)
