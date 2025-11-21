"""
Integration tests for Template building operations.

Tests cover:
- Creating templates from base images
- Building templates with steps
- Creating sandboxes from custom templates
"""

import os
import pytest
import time
from hopx_ai import Template, AsyncSandbox
from hopx_ai.template import BuildOptions, wait_for_port

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")


@pytest.fixture
def api_key():
    """Get API key from environment."""
    key = os.getenv("HOPX_API_KEY")
    if not key:
        pytest.skip("HOPX_API_KEY environment variable not set")
    return key


@pytest.fixture
def template_name():
    """Generate unique template name for testing."""
    return f"test-template-{int(time.time())}"


class TestTemplateBuilding:
    """Test Template building operations."""

    @pytest.mark.asyncio
    async def test_create_simple_template(self, api_key, template_name):
        """Test creating a simple template."""
        # Define a simple template
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("pip install requests")
            .set_env("TEST_VAR", "test_value")
        )

        # Build the template
        result = await Template.build(
            template,
            BuildOptions(
                name=template_name,
                api_key=api_key,
                base_url=BASE_URL,
                cpu=1,
                memory=1024,
                disk_gb=5,
            ),
        )

        assert result.template_id is not None
        assert result.build_id is not None
        assert result.duration > 0

        # Cleanup: Delete the template
        try:
            await AsyncSandbox.delete_template(
                template_id=result.template_id,
                api_key=api_key,
                base_url=BASE_URL,
            )
        except Exception:
            pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_create_template_with_start_cmd(self, api_key, template_name):
        """Test creating template with start command and ready check."""
        # Define template with start command
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("mkdir -p /app")
            .set_workdir("/app")
            .run_cmd("""cat > main.py << 'EOF'
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

PORT = int(os.environ.get("PORT", 8000))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Hello</h1>")
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()
EOF""")
            .set_env("PORT", "8000")
            .set_start_cmd("python main.py", wait_for_port(8000))
        )

        # Build the template
        result = await Template.build(
            template,
            BuildOptions(
                name=template_name,
                api_key=api_key,
                base_url=BASE_URL,
                cpu=1,
                memory=1024,
                disk_gb=5,
            ),
        )

        assert result.template_id is not None

        # Create sandbox from template
        sandbox = await AsyncSandbox.create(
            template=template_name,
            api_key=api_key,
            base_url=BASE_URL,
        )

        try:
            # Verify sandbox is running
            info = await sandbox.get_info()
            assert info.status == "running"
        finally:
            await sandbox.kill()
            # Cleanup template
            try:
                await AsyncSandbox.delete_template(
                    template_id=result.template_id,
                    api_key=api_key,
                    base_url=BASE_URL,
                )
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_template_from_ubuntu(self, api_key, template_name):
        """Test creating template from Ubuntu base image."""
        template = (
            Template()
            .from_ubuntu_image("22.04")
            .run_cmd("apt-get update")
            .run_cmd("apt-get install -y curl")
        )

        result = await Template.build(
            template,
            BuildOptions(
                name=template_name,
                api_key=api_key,
                base_url=BASE_URL,
                cpu=1,
                memory=1024,
                disk_gb=5,
            ),
        )

        assert result.template_id is not None

        # Cleanup
        try:
            await AsyncSandbox.delete_template(
                template_id=result.template_id,
                api_key=api_key,
                base_url=BASE_URL,
            )
        except Exception:
            pass

