"""
Integration tests for AsyncSandbox token management operations.

Tests cover:
- Refreshing JWT token (async)
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


class TestAsyncTokenManagement:
    """Test async token management operations."""

    @pytest.mark.asyncio
    async def test_refresh_token(self, sandbox):
        """Test refreshing JWT token."""
        # Access agent to ensure token is generated
        await sandbox.get_info()
        
        # Refresh token
        await sandbox.refresh_token()
        
        # Verify token refresh succeeded (no error)
        # Token should still be accessible
        info = await sandbox.get_info()
        assert info is not None

