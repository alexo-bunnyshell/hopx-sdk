"""
Integration tests for Template ready check functions.

Tests cover:
- wait_for_port
- wait_for_url
- wait_for_file
- wait_for_process
- wait_for_command
"""

import os
import pytest
import time
from hopx_ai import Template, AsyncSandbox
from hopx_ai.template import BuildOptions, wait_for_port, wait_for_url, wait_for_file, wait_for_process, wait_for_command

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
    return f"test-ready-check-{int(time.time())}"


class TestTemplateReadyChecks:
    """Test Template ready check functions."""

    @pytest.mark.asyncio
    async def test_wait_for_port(self, api_key, template_name):
        """Test wait_for_port ready check."""
        # Create template with a service that listens on a port
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("mkdir -p /app")
            .set_workdir("/app")
            .run_cmd("""cat > server.py << 'EOF'
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

PORT = int(os.environ.get("PORT", 8000))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()
EOF""")
            .set_env("PORT", "8000")
            .set_start_cmd("python server.py", wait_for_port(8000))
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

    @pytest.mark.asyncio
    async def test_wait_for_url(self, api_key, template_name):
        """Test wait_for_url ready check."""
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("mkdir -p /app")
            .set_workdir("/app")
            .run_cmd("""cat > server.py << 'EOF'
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

PORT = int(os.environ.get("PORT", 8000))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()
EOF""")
            .set_env("PORT", "8000")
            .set_start_cmd("python server.py", wait_for_url("http://localhost:8000"))
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

    @pytest.mark.asyncio
    async def test_wait_for_file(self, api_key, template_name):
        """Test wait_for_file ready check."""
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("mkdir -p /app")
            .set_workdir("/app")
            .run_cmd("""cat > start.sh << 'EOF'
#!/bin/bash
sleep 2
echo "ready" > /app/ready.txt
python -m http.server 8000
EOF""")
            .run_cmd("chmod +x start.sh")
            .set_start_cmd("/app/start.sh", wait_for_file("/app/ready.txt"))
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

    @pytest.mark.asyncio
    async def test_wait_for_process(self, api_key, template_name):
        """Test wait_for_process ready check."""
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("mkdir -p /app")
            .set_workdir("/app")
            .run_cmd("""cat > start.sh << 'EOF'
#!/bin/bash
python -m http.server 8000 &
echo $! > /app/server.pid
wait
EOF""")
            .run_cmd("chmod +x start.sh")
            .set_start_cmd("/app/start.sh", wait_for_process("python"))
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

    @pytest.mark.asyncio
    async def test_wait_for_command(self, api_key, template_name):
        """Test wait_for_command ready check."""
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("mkdir -p /app")
            .set_workdir("/app")
            .run_cmd("""cat > init.sh << 'EOF'
#!/bin/bash
echo "Initializing..."
sleep 1
echo "Ready"
exit 0
EOF""")
            .run_cmd("chmod +x init.sh")
            .set_start_cmd("python -m http.server 8000", wait_for_command("/app/init.sh"))
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

