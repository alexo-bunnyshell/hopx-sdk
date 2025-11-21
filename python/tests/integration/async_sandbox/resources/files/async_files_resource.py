"""
Integration tests for AsyncSandbox Files resource.

Tests cover:
- Writing and reading files (async)
- Listing files (async)
- File existence checks (async)
- Creating directories (async)
- Removing files (async)
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


class TestAsyncFilesResource:
    """Test async file operations."""

    @pytest.mark.asyncio
    async def test_write_and_read_file(self, sandbox):
        """Test writing and reading a file."""
        content = "Hello, World!\nThis is a test file."
        path = "/workspace/test.txt"

        await sandbox.files.write(path, content)
        read_content = await sandbox.files.read(path)

        assert read_content == content

    @pytest.mark.asyncio
    async def test_list_files(self, sandbox):
        """Test listing files in a directory."""
        # Create a test file
        await sandbox.files.write("/workspace/test_list.txt", "test")

        files = await sandbox.files.list("/workspace")

        assert isinstance(files, list)

    @pytest.mark.asyncio
    async def test_file_exists(self, sandbox):
        """Test checking if file exists."""
        path = "/workspace/test_exists.txt"

        # File shouldn't exist initially
        assert await sandbox.files.exists(path) is False

        # Create file
        await sandbox.files.write(path, "test")
        assert await sandbox.files.exists(path) is True

    @pytest.mark.asyncio
    async def test_mkdir(self, sandbox):
        """Test creating a directory."""
        dir_path = "/workspace/test_dir"

        await sandbox.files.mkdir(dir_path)
        assert await sandbox.files.exists(dir_path) is True

    @pytest.mark.asyncio
    async def test_remove_file(self, sandbox):
        """Test removing a file."""
        path = "/workspace/test_remove.txt"

        # Create file
        await sandbox.files.write(path, "test")
        assert await sandbox.files.exists(path) is True

        # Remove file
        await sandbox.files.remove(path)
        assert await sandbox.files.exists(path) is False

