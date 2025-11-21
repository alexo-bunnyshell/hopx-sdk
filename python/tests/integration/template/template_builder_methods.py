"""
Integration tests for Template builder methods.

Tests cover:
- Template builder methods (from_node_image, git_clone, etc.)
- Template getter methods
"""

import os
import pytest
import time
from hopx_ai import Template, AsyncSandbox
from hopx_ai.template import BuildOptions

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
    return f"test-builder-{int(time.time())}"


class TestTemplateBuilderMethods:
    """Test Template builder methods."""

    def test_from_node_image(self):
        """Test creating template from Node.js base image."""
        template = Template().from_node_image("20")
        
        assert template.get_from_image() is not None
        assert "node" in template.get_from_image().lower() or "20" in template.get_from_image()

    def test_template_getter_methods(self):
        """Test template getter methods."""
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("pip install requests")
            .set_env("TEST_VAR", "test_value")
            .set_workdir("/app")
            .set_start_cmd("python app.py")
        )

        # Test getters
        assert template.get_from_image() is not None
        assert "python" in template.get_from_image().lower()
        
        steps = template.get_steps()
        assert isinstance(steps, list)
        assert len(steps) > 0
        
        start_cmd = template.get_start_cmd()
        assert start_cmd == "python app.py"
        
        ready_check = template.get_ready_check()
        assert ready_check is None  # No ready check set

    def test_template_builder_chaining(self):
        """Test template builder method chaining."""
        template = (
            Template()
            .from_ubuntu_image("22.04")
            .apt_install("curl", "git")
            .run_cmd("mkdir -p /app")
            .set_workdir("/app")
            .set_env("NODE_ENV", "production")
            .set_envs({"VAR1": "val1", "VAR2": "val2"})
        )

        steps = template.get_steps()
        assert len(steps) > 0
        # Should have apt_install and run_cmd steps

    @pytest.mark.asyncio
    async def test_template_with_git_clone(self, api_key, template_name):
        """Test template with git clone."""
        # Use a small public repo for testing
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("apt-get update && apt-get install -y git")
            .git_clone("https://github.com/python/cpython.git", "/tmp/cpython")
            .run_cmd("ls /tmp/cpython")
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

    def test_template_skip_cache(self):
        """Test template skip_cache method."""
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("pip install requests")
            .skip_cache()  # Skip cache for last step
        )

        steps = template.get_steps()
        if steps:
            # Last step should have skip_cache set
            assert hasattr(steps[-1], "skip_cache") or steps[-1].get("skip_cache") is True

