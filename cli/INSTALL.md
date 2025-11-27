# Hopx CLI Installation Guide

This guide covers installing, updating, and uninstalling the Hopx CLI.

## Quick Install

### One-Line Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/hopx-ai/hopx/main/cli/scripts/install.sh | bash
```

This script will:
1. Detect your OS (Linux, macOS) and architecture (x64, arm64)
2. Install Python 3.12+ if needed (auto-install, no prompt)
3. Install the Hopx CLI via pip
4. Configure your PATH for bash, zsh, or fish
5. Verify the installation

### Alternative: Manual Install

```bash
pip install hopx-cli
```

Or with pipx (isolated installation):

```bash
pipx install hopx-cli
```

## Requirements

- **Python**: 3.12 or higher
- **Operating System**: Linux, macOS, or Windows (WSL)
- **Network**: HTTPS access to PyPI and api.hopx.dev

## Installation Methods

### Method 1: One-Line Installer (Recommended)

The one-line installer is the easiest way to get started.

```bash
curl -fsSL https://raw.githubusercontent.com/hopx-ai/hopx/main/cli/scripts/install.sh | bash
```

**Options:**

```bash
# Dry run (see what would happen without making changes)
curl -fsSL https://get.hopx.ai/install.sh | bash -s -- --dry-run

# Install using pipx instead of pip
curl -fsSL https://get.hopx.ai/install.sh | bash -s -- --mode pipx

# Install development version from GitHub
curl -fsSL https://get.hopx.ai/install.sh | bash -s -- --mode git
```

**Environment Variables:**

```bash
# Control installation mode
export HOPX_INSTALL_MODE=pipx  # pip (default), pipx, git
curl -fsSL https://get.hopx.ai/install.sh | bash

# Dry run mode
export HOPX_DRY_RUN=true
curl -fsSL https://get.hopx.ai/install.sh | bash
```

### Method 2: uv (Recommended)

[uv](https://docs.astral.sh/uv/) is a fast Python package manager. Install as a global tool:

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Hopx CLI as a tool
uv tool install hopx-cli

# Upgrade
uv tool upgrade hopx-cli
```

**Benefits of uv:**
- 10-100x faster than pip
- Isolated tool environment (like pipx)
- Automatic PATH management
- No dependency conflicts

### Method 3: pip (Standard)

Install from PyPI:

```bash
# User-level installation (no sudo required)
pip install --user hopx-cli

# System-wide installation
sudo pip install hopx-cli

# Upgrade existing installation
pip install --upgrade hopx-cli
```

### Method 4: pipx (Isolated)

Install in an isolated environment:

```bash
# Install pipx if not already installed
pip install --user pipx
pipx ensurepath

# Install Hopx CLI
pipx install hopx-cli

# Upgrade
pipx upgrade hopx-cli
```

**Benefits of pipx:**
- Isolated from system Python packages
- No dependency conflicts
- Clean uninstallation
- Automatic PATH management

### Method 5: Development Install

Install the latest development version:

**With uv (recommended):**

```bash
git clone https://github.com/hopx-ai/hopx.git
cd hopx/cli
uv sync --all-extras
source .venv/bin/activate
```

**With pip:**

```bash
# From GitHub
pip install git+https://github.com/hopx-ai/hopx.git#subdirectory=cli

# From local clone
git clone https://github.com/hopx-ai/hopx.git
cd hopx/cli
pip install -e ".[dev]"
```

## Platform-Specific Instructions

### Linux

#### Debian/Ubuntu

```bash
# Update package list
sudo apt-get update

# Install Python 3.12+ if needed
sudo apt-get install -y python3.12 python3.12-venv python3-pip

# Install Hopx CLI
pip install --user hopx-cli
```

#### RHEL/CentOS/Fedora

```bash
# Install Python 3.12+ if needed
sudo yum install -y python3.12 python3-pip

# Install Hopx CLI
pip install --user hopx-cli
```

#### Arch Linux

```bash
# Install Python if needed
sudo pacman -S python python-pip

# Install Hopx CLI
pip install --user hopx-cli
```

### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.12+ if needed
brew install python@3.12

# Install Hopx CLI
pip3 install --user hopx-cli
```

### Windows (WSL)

Windows users should use WSL (Windows Subsystem for Linux):

```bash
# In WSL terminal
curl -fsSL https://get.hopx.ai/install.sh | bash
```

Or install manually:

```bash
pip install --user hopx-cli
```

## Post-Installation

### Verify Installation

```bash
hopx --version
```

Expected output:
```
Hopx CLI v0.1.0
```

### Configure API Key

Get your API key from [https://hopx.ai/dashboard](https://hopx.ai/dashboard)

Set it as an environment variable:

```bash
export HOPX_API_KEY="hopx_live_..."
```

Make it permanent by adding to your shell config:

```bash
# For bash
echo 'export HOPX_API_KEY="hopx_live_..."' >> ~/.bashrc
source ~/.bashrc

# For zsh
echo 'export HOPX_API_KEY="hopx_live_..."' >> ~/.zshrc
source ~/.zshrc
```

### Test Installation

```bash
# Run a simple command
hopx run "print('Hello from Hopx!')"

# Check system health
hopx system health

# List available templates
hopx template list
```

## Troubleshooting

### Command Not Found

If `hopx` is not found after installation:

**1. Check if installed:**

```bash
pip show hopx-cli
```

**2. Find installation location:**

```bash
python3 -m site --user-base
```

**3. Add to PATH:**

```bash
# Get user base directory
USER_BASE=$(python3 -m site --user-base)

# Add to PATH in your shell config
echo "export PATH=\"\$PATH:\$USER_BASE/bin\"" >> ~/.bashrc
source ~/.bashrc
```

### Python Version Too Old

If you have Python < 3.12:

**Ubuntu/Debian:**

```bash
sudo apt-get install -y python3.12 python3.12-venv
```

**macOS:**

```bash
brew install python@3.12
```

**Or install from source:**

Download from [python.org/downloads](https://www.python.org/downloads/)

### Permission Denied

If you get permission errors:

```bash
# Use user-level installation (no sudo)
pip install --user hopx-cli

# Or use pipx
pipx install hopx-cli
```

### SSL Certificate Errors

If you get SSL errors:

```bash
# Upgrade pip first
pip install --upgrade pip

# Try with trusted host
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org hopx-cli
```

### Installation Verification Fails

If installation completes but verification fails:

```bash
# Restart terminal
# Or reload shell config
source ~/.bashrc  # or ~/.zshrc

# Verify Python can import the package
python3 -c "import hopx_cli; print('OK')"

# Check PATH
echo $PATH | grep -o '[^:]*bin[^:]*'
```

## Updating

### Update to Latest Version

```bash
# Using uv
uv tool upgrade hopx-cli

# Using pip
pip install --upgrade hopx-cli

# Using pipx
pipx upgrade hopx-cli

# Check new version
hopx --version
```

### Update to Specific Version

```bash
# Using uv
uv tool install hopx-cli==0.1.0

# Using pip
pip install hopx-cli==0.1.0
```

### Update via Self-Update Command (Recommended)

```bash
# Update to latest version
hopx self-update

# Check for updates without installing
hopx self-update --check

# Update to specific version
hopx self-update --version 0.2.0
```

### Update via Installer

```bash
# Re-run installer (it will upgrade)
curl -fsSL https://raw.githubusercontent.com/hopx-ai/hopx/main/cli/scripts/install.sh | bash
```

## Uninstallation

### One-Line Uninstaller

```bash
curl -fsSL https://raw.githubusercontent.com/hopx-ai/hopx/main/cli/scripts/uninstall.sh | bash
```

This will:
1. Remove the Hopx CLI package
2. Optionally remove configuration files
3. Optionally remove cache
4. Clean up PATH entries
5. Verify uninstallation

**Options:**

```bash
# Dry run
curl -fsSL https://raw.githubusercontent.com/hopx-ai/hopx/main/cli/scripts/uninstall.sh | bash -s -- --dry-run

# Full cleanup without prompts (removes config and cache)
curl -fsSL https://raw.githubusercontent.com/hopx-ai/hopx/main/cli/scripts/uninstall.sh | bash -s -- --full
```

### Manual Uninstall

```bash
# Using uv
uv tool uninstall hopx-cli

# Using pip
pip uninstall hopx-cli

# Using pipx
pipx uninstall hopx-cli
```

### Remove Configuration Files

```bash
# Remove config directory
rm -rf ~/.config/hopx

# Remove cache
rm -rf ~/.cache/hopx

# Remove config files
rm -f ~/.hopxrc ~/.hopx.yaml
```

### Clean PATH Entries

Remove Hopx-related PATH entries from:
- `~/.bashrc`
- `~/.zshrc`
- `~/.profile`

Look for lines like:
```bash
# Added by Hopx CLI installer
export PATH="$PATH:/path/to/bin"
```

## Advanced Installation

### Behind a Proxy

```bash
# Set proxy environment variables
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"

# Install
pip install hopx-cli
```

### Offline Installation

```bash
# On a machine with internet, download the package
pip download hopx-cli -d hopx-packages/

# Transfer hopx-packages/ to offline machine
# Then install
pip install --no-index --find-links hopx-packages/ hopx-cli
```

### Custom Installation Location

```bash
# Install to specific directory
pip install --target=/custom/path hopx-cli

# Add to PATH
export PATH="$PATH:/custom/path"
```

### Virtual Environment

**With uv:**

```bash
# Create and install in one command
uv venv hopx-venv --python 3.12
uv pip install hopx-cli --python hopx-venv/bin/python

# Activate
source hopx-venv/bin/activate
```

**With venv:**

```bash
# Create virtual environment
python3 -m venv hopx-venv

# Activate
source hopx-venv/bin/activate  # Linux/macOS
# hopx-venv\Scripts\activate    # Windows

# Install
pip install hopx-cli

# Deactivate when done
deactivate
```

## CI/CD Integration

The installer supports non-interactive mode for CI/CD pipelines.

### Environment Variables

```bash
# Skip all interactive prompts
export HOPX_NON_INTERACTIVE=true

# Skip PATH setup (useful in containers with custom PATH)
export HOPX_SKIP_PATH_SETUP=true

# Suppress output except errors
export HOPX_QUIET=true

# Preview what would happen without making changes
export HOPX_DRY_RUN=true

# Choose installation method: pip (default), pipx, uv
export HOPX_INSTALL_MODE=pip
```

### GitHub Actions

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Hopx CLI
        env:
          HOPX_NON_INTERACTIVE: "true"
        run: |
          curl -fsSL https://raw.githubusercontent.com/hopx-ai/hopx/main/cli/scripts/install.sh | bash
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Verify installation
        run: hopx --version

      - name: Run tests
        env:
          HOPX_API_KEY: ${{ secrets.HOPX_API_KEY }}
        run: hopx system health
```

### GitLab CI

```yaml
test:
  image: python:3.12
  variables:
    HOPX_NON_INTERACTIVE: "true"
  before_script:
    - curl -fsSL https://raw.githubusercontent.com/hopx-ai/hopx/main/cli/scripts/install.sh | bash
    - export PATH="$HOME/.local/bin:$PATH"
  script:
    - hopx --version
    - hopx system health
```

### Docker

```dockerfile
FROM python:3.12-slim

# Install Hopx CLI
ENV HOPX_NON_INTERACTIVE=true
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://raw.githubusercontent.com/hopx-ai/hopx/main/cli/scripts/install.sh | bash \
    && apt-get remove -y curl && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

# Verify installation
RUN hopx --version
```

### CircleCI

```yaml
version: 2.1

jobs:
  test:
    docker:
      - image: python:3.12
    steps:
      - checkout
      - run:
          name: Install Hopx CLI
          environment:
            HOPX_NON_INTERACTIVE: "true"
          command: |
            curl -fsSL https://raw.githubusercontent.com/hopx-ai/hopx/main/cli/scripts/install.sh | bash
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> $BASH_ENV
      - run:
          name: Verify installation
          command: hopx --version
```

## Security Considerations

### Verify Installer Script

Before running the installer, review it:

```bash
curl -fsSL https://raw.githubusercontent.com/hopx-ai/hopx/main/cli/scripts/install.sh | less
```

### Checksums

Verify package integrity:

```bash
# Download and verify
pip download hopx-cli
pip hash hopx-cli-*.whl
```

### Secure API Keys

Never commit API keys to version control:

```bash
# Use environment variables
export HOPX_API_KEY="..."

# Or use a .env file (add to .gitignore)
echo "HOPX_API_KEY=..." > .env
echo ".env" >> .gitignore
```

## Support

If you encounter issues:

1. **Check documentation**: [https://docs.hopx.ai/cli](https://docs.hopx.ai/cli)
2. **Search issues**: [https://github.com/hopx-ai/hopx/issues](https://github.com/hopx-ai/hopx/issues)
3. **Discord**: [https://discord.gg/hopx](https://discord.gg/hopx)
4. **Email**: support@hopx.ai

When reporting issues, include:
- Operating system and version
- Python version (`python3 --version`)
- Installation method used
- Full error message
- Output of `pip show hopx-cli`

## Next Steps

After installation:

1. Set your API key (see "Configure API Key" above)
2. Read the [Quick Start Guide](README.md#quick-start)
3. View available commands with `hopx --help`
4. Join our [Discord community](https://discord.gg/hopx)

Happy coding with Hopx!
