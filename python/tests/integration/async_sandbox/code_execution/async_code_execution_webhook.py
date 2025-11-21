"""
Integration tests for AsyncSandbox async code execution with webhook callback.

Tests cover:
- Executing code asynchronously with webhook callback (async)
"""

import os
import pytest
from hopx_ai import AsyncSandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


@pytest.fixture
def api_key():
    """Get API key from environment."""
    key = os.getenv("HOPX_API_KEY")
    if not key:
        pytest.skip("HOPX_API_KEY environment variable not set")
    return key


@pytest.fixture
async def sandbox(api_key):
    """Create a sandbox for testing and clean up after."""
    sandbox = await AsyncSandbox.create(
        template=TEST_TEMPLATE,
        api_key=api_key,
        base_url=BASE_URL,
    )
    yield sandbox
    try:
        await sandbox.kill()
    except Exception:
        pass


class TestAsyncCodeExecutionWebhook:
    """Test async code execution with webhook callback."""

    @pytest.mark.asyncio
    async def test_run_code_async(self, sandbox):
        """Test executing code asynchronously with webhook callback."""
        # Use a test webhook URL
        callback_url = "https://httpbin.org/post"
        
        execution_id = await sandbox.run_code_async(
            code="print('Hello from async execution')",
            callback_url=callback_url,
            language="python",
            timeout_seconds=1800,
        )

        assert isinstance(execution_id, str)
        assert len(execution_id) > 0

