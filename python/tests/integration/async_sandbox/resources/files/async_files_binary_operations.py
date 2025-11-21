"""
Integration tests for AsyncSandbox Files resource binary operations.

Tests cover:
- Reading binary files (async)
- Writing binary files (async)
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


class TestAsyncFilesBinaryOperations:
    """Test async binary file operations."""

    @pytest.mark.asyncio
    async def test_read_bytes(self, sandbox):
        """Test reading binary file contents."""
        # Create a binary file first using code execution
        await sandbox.run_code(
            """
with open('/workspace/test.bin', 'wb') as f:
    f.write(b'\\x00\\x01\\x02\\x03\\xFF\\xFE\\xFD')
"""
        )

        # Read binary file
        content = await sandbox.files.read_bytes("/workspace/test.bin")
        assert isinstance(content, bytes)
        assert content == b'\x00\x01\x02\x03\xFF\xFE\xFD'

    @pytest.mark.asyncio
    async def test_write_bytes(self, sandbox):
        """Test writing binary file contents."""
        binary_data = b'\x00\x01\x02\x03\xFF\xFE\xFD\xAA\xBB\xCC'
        path = "/workspace/test_write.bin"

        await sandbox.files.write_bytes(path, binary_data)
        
        # Verify by reading back
        read_content = await sandbox.files.read_bytes(path)
        assert read_content == binary_data

