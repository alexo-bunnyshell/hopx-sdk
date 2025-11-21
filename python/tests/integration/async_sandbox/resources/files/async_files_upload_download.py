"""
Integration tests for AsyncSandbox Files resource upload/download operations.

Tests cover:
- Uploading files from local filesystem to sandbox (async)
- Downloading files from sandbox to local filesystem (async)
"""

import os
import pytest
import tempfile
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


class TestAsyncFilesUploadDownload:
    """Test async file upload and download operations."""

    @pytest.mark.asyncio
    async def test_upload_text_file(self, sandbox):
        """Test uploading a text file from local filesystem."""
        # Create a temporary local file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            local_path = f.name
            f.write("Hello from local file!\nThis is a test upload.")
        
        try:
            # Upload to sandbox
            remote_path = "/workspace/uploaded_file.txt"
            await sandbox.files.upload(local_path, remote_path)
            
            # Verify file was uploaded
            assert await sandbox.files.exists(remote_path) is True
            content = await sandbox.files.read(remote_path)
            assert "Hello from local file!" in content
        finally:
            # Cleanup local file
            os.unlink(local_path)

    @pytest.mark.asyncio
    async def test_download_text_file(self, sandbox):
        """Test downloading a text file from sandbox to local filesystem."""
        # Create a file in sandbox first
        remote_path = "/workspace/download_test.txt"
        test_content = "This file will be downloaded\nLine 2\nLine 3"
        await sandbox.files.write(remote_path, test_content)
        
        # Download to local filesystem
        with tempfile.NamedTemporaryFile(mode='r', delete=False, suffix='.txt') as f:
            local_path = f.name
        
        try:
            await sandbox.files.download(remote_path, local_path)
            
            # Verify file was downloaded
            assert os.path.exists(local_path)
            with open(local_path, 'r') as f:
                downloaded_content = f.read()
            assert downloaded_content == test_content
        finally:
            # Cleanup local file
            if os.path.exists(local_path):
                os.unlink(local_path)

