"""Tests for async operation helpers.

Tests cover:
- run_async decorator for sync/async bridge
- run_with_timeout utility
- gather_with_concurrency utility
"""

from __future__ import annotations

import asyncio

import pytest


class TestRunAsyncDecorator:
    """Tests for run_async decorator."""

    @pytest.mark.unit
    def test_runs_async_function_synchronously(self) -> None:
        """Allows calling async function without await."""
        from hopx_cli.core.async_helpers import run_async

        @run_async
        async def async_func() -> str:
            return "hello"

        result = async_func()
        assert result == "hello"

    @pytest.mark.unit
    def test_passes_arguments(self) -> None:
        """Passes positional and keyword arguments."""
        from hopx_cli.core.async_helpers import run_async

        @run_async
        async def async_func(a: int, b: int, c: int = 0) -> int:
            return a + b + c

        result = async_func(1, 2, c=3)
        assert result == 6

    @pytest.mark.unit
    def test_propagates_exceptions(self) -> None:
        """Propagates exceptions from async function."""
        from hopx_cli.core.async_helpers import run_async

        @run_async
        async def async_func() -> None:
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            async_func()

    @pytest.mark.unit
    def test_propagates_keyboard_interrupt(self) -> None:
        """Propagates KeyboardInterrupt to caller."""
        from hopx_cli.core.async_helpers import run_async

        @run_async
        async def async_func() -> None:
            raise KeyboardInterrupt()

        with pytest.raises(KeyboardInterrupt):
            async_func()

    @pytest.mark.unit
    def test_preserves_function_metadata(self) -> None:
        """Preserves original function name and docstring."""
        from hopx_cli.core.async_helpers import run_async

        @run_async
        async def my_function() -> None:
            """My docstring."""
            pass

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."

    @pytest.mark.unit
    def test_returns_async_result(self) -> None:
        """Returns awaited result correctly."""
        from hopx_cli.core.async_helpers import run_async

        @run_async
        async def async_func() -> dict[str, int]:
            await asyncio.sleep(0)
            return {"value": 42}

        result = async_func()
        assert result == {"value": 42}


class TestRunWithTimeout:
    """Tests for run_with_timeout function."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_returns_result_before_timeout(self) -> None:
        """Returns coroutine result when completed before timeout."""
        from hopx_cli.core.async_helpers import run_with_timeout

        async def fast_coro() -> str:
            return "done"

        result = await run_with_timeout(fast_coro(), timeout=5.0)
        assert result == "done"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_raises_on_timeout(self) -> None:
        """Raises TimeoutError when operation times out."""
        from hopx_cli.core.async_helpers import run_with_timeout

        async def slow_coro() -> str:
            await asyncio.sleep(10)
            return "done"

        with pytest.raises(asyncio.TimeoutError):
            await run_with_timeout(slow_coro(), timeout=0.01)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_propagates_exception(self) -> None:
        """Propagates exception from coroutine."""
        from hopx_cli.core.async_helpers import run_with_timeout

        async def failing_coro() -> None:
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError, match="fail"):
            await run_with_timeout(failing_coro(), timeout=5.0)


class TestGatherWithConcurrency:
    """Tests for gather_with_concurrency function."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_runs_tasks_concurrently(self) -> None:
        """Runs multiple tasks with limited concurrency."""
        from hopx_cli.core.async_helpers import gather_with_concurrency

        results: list[int] = []

        async def task(n: int) -> int:
            await asyncio.sleep(0)
            results.append(n)
            return n * 2

        output = await gather_with_concurrency(2, task(1), task(2), task(3))

        assert output == [2, 4, 6]
        assert set(results) == {1, 2, 3}

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_limits_concurrency(self) -> None:
        """Limits number of concurrent tasks."""
        from hopx_cli.core.async_helpers import gather_with_concurrency

        active = 0
        max_active = 0

        async def task() -> None:
            nonlocal active, max_active
            active += 1
            max_active = max(max_active, active)
            await asyncio.sleep(0.01)
            active -= 1

        await gather_with_concurrency(2, task(), task(), task(), task())

        assert max_active <= 2

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_returns_results_in_order(self) -> None:
        """Returns results in same order as tasks."""
        from hopx_cli.core.async_helpers import gather_with_concurrency

        async def task(n: int) -> int:
            await asyncio.sleep(0.01 * (3 - n))  # Vary sleep time
            return n

        results = await gather_with_concurrency(3, task(1), task(2), task(3))

        assert results == [1, 2, 3]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handles_empty_tasks(self) -> None:
        """Handles empty task list."""
        from hopx_cli.core.async_helpers import gather_with_concurrency

        results = await gather_with_concurrency(2)
        assert results == []

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_single_concurrency(self) -> None:
        """Runs tasks sequentially with concurrency=1."""
        from hopx_cli.core.async_helpers import gather_with_concurrency

        order: list[int] = []

        async def task(n: int) -> int:
            order.append(n)
            await asyncio.sleep(0)
            return n

        await gather_with_concurrency(1, task(1), task(2), task(3))

        # With concurrency=1, tasks start in order
        assert order == [1, 2, 3]
