"""
Integration tests for AsyncSandbox token management operations.

Tests cover:
- Refreshing JWT token (async)
"""

import os
import pytest
from hopx_ai import AsyncSandbox
from hopx_ai._token_cache import get_cached_token

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
        
        # Get initial token from cache
        initial_token_data = get_cached_token(sandbox.sandbox_id)
        assert initial_token_data is not None, "Token should exist after get_info()"
        initial_token = initial_token_data.token
        initial_expires_at = initial_token_data.expires_at
        
        # Verify initial token is valid
        assert isinstance(initial_token, str)
        assert len(initial_token) > 0
        # JWT tokens typically start with "eyJ" (base64 encoded JSON)
        assert initial_token.startswith("eyJ") or len(initial_token) > 20
        
        # Refresh token
        await sandbox.refresh_token()
        
        # Get new token from cache
        new_token_data = get_cached_token(sandbox.sandbox_id)
        assert new_token_data is not None, "Token should exist after refresh"
        new_token = new_token_data.token
        new_expires_at = new_token_data.expires_at
        
        # Verify new token is valid
        assert isinstance(new_token, str)
        assert len(new_token) > 0
        assert new_token.startswith("eyJ") or len(new_token) > 20
        
        # Verify token was refreshed (new expiration time should be later)
        assert new_expires_at > initial_expires_at, \
            "New token should have later expiration time after refresh"
        
        # Verify sandbox still works with refreshed token
        info = await sandbox.get_info()
        assert info is not None

