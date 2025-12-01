# Hopx CLI Installation Scripts

This directory contains installation and uninstallation scripts for the Hopx CLI.

## Scripts

### install.sh

One-line installer for the Hopx CLI. Automatically detects your OS, Python version, and installs the CLI.

**Quick Install:**
```bash
curl -fsSL https://get.hopx.ai/install.sh | bash
```

**Local Testing:**
```bash
# Dry run (no changes)
bash scripts/install.sh --dry-run

# Install via pip (default)
bash scripts/install.sh

# Install via pipx (isolated)
bash scripts/install.sh --mode pipx

# Install development version from GitHub
bash scripts/install.sh --mode git
```

**Environment Variables:**
- `HOPX_INSTALL_MODE`: Installation mode (`pip`, `pipx`, `git`)
- `HOPX_DRY_RUN`: Set to `true` for dry run

**Features:**
- Cross-platform: Linux (Debian/Ubuntu, RHEL/CentOS, Arch), macOS
- Python 3.12+ detection with automatic installation offer
- Multiple installation methods: pip, pipx, git
- PATH configuration
- Installation verification
- Quick start guide

### uninstall.sh

Complete uninstaller for the Hopx CLI. Removes the package, configuration, and cache.

**Quick Uninstall:**
```bash
curl -fsSL https://get.hopx.ai/uninstall.sh | bash
```

**Local Testing:**
```bash
# Dry run (no changes)
bash scripts/uninstall.sh --dry-run

# Interactive uninstall (prompts for config/cache)
bash scripts/uninstall.sh

# Full cleanup without prompts
bash scripts/uninstall.sh --full
```

**Environment Variables:**
- `HOPX_DRY_RUN`: Set to `true` for dry run

**Features:**
- Removes pip/pipx installations
- Optional config cleanup (`~/.config/hopx`, `~/.hopxrc`)
- Optional cache cleanup (`~/.cache/hopx`)
- PATH cleanup from shell configs
- Uninstallation verification

## Development

### Testing Locally

Both scripts support dry-run mode for safe testing:

```bash
# Test install
bash scripts/install.sh --dry-run

# Test uninstall
bash scripts/uninstall.sh --dry-run

# Test different modes
bash scripts/install.sh --dry-run --mode pipx
bash scripts/install.sh --dry-run --mode git
```

### Script Structure

Both scripts follow this pattern:

1. **Header**: Version info, colors, configuration
2. **Logging**: Colored output functions (all to stderr)
3. **Utilities**: OS detection, command checks, version comparison
4. **Core Functions**: Installation/uninstallation logic
5. **Verification**: Check success
6. **User Guidance**: Quick start or feedback

### Color Codes

Scripts use ANSI color codes:
- `BLUE`: Info messages
- `GREEN`: Success messages
- `YELLOW`: Warning messages
- `RED`: Error messages
- `CYAN`: Step headers

All output goes to stderr to avoid interfering with command substitution.

### Error Handling

Scripts use `set -euo pipefail` for strict error handling:
- `-e`: Exit on error
- `-u`: Error on undefined variables
- `-o pipefail`: Catch errors in pipes

## Deployment

### GitHub Release

These scripts should be:
1. Included in GitHub releases
2. Hosted at `https://get.hopx.ai/install.sh` and `https://get.hopx.ai/uninstall.sh`
3. Tested on multiple platforms before release

### Testing Checklist

Before deploying, test on:
- [ ] Ubuntu 22.04 LTS (x64, ARM64)
- [ ] Debian 12
- [ ] macOS (Intel, Apple Silicon)
- [ ] RHEL/CentOS 8+
- [ ] Arch Linux

Test scenarios:
- [ ] Fresh install
- [ ] Upgrade existing installation
- [ ] Install with Python 3.12
- [ ] Install with Python 3.13
- [ ] Install without Python (auto-install)
- [ ] pip mode
- [ ] pipx mode
- [ ] git mode
- [ ] Uninstall with config cleanup
- [ ] Uninstall without config cleanup

## Security

### Best Practices

1. **HTTPS Only**: Always use HTTPS URLs
2. **No Sudo by Default**: Only request sudo when necessary
3. **User Confirmation**: Prompt before major actions
4. **Clear Messages**: Explain what will happen
5. **Dry Run Available**: Let users test without changes

### Checksum Verification

For future enhancement, add checksum verification:
```bash
# Example (not implemented yet)
EXPECTED_SHA256="..."
ACTUAL_SHA256=$(sha256sum hopx-cli.tar.gz | awk '{print $1}')
if [[ "$EXPECTED_SHA256" != "$ACTUAL_SHA256" ]]; then
    log_error "Checksum mismatch!"
    exit 1
fi
```

## Troubleshooting

### Common Issues

**Command not found after install:**
```bash
# Reload shell config
source ~/.bashrc  # or ~/.zshrc

# Or restart terminal
```

**Permission denied:**
```bash
# Use user-level install
pip install --user hopx-cli
```

**Python version too old:**
```bash
# Install Python 3.12+ first
# Ubuntu/Debian:
sudo apt-get install python3.12

# macOS:
brew install python@3.12
```

**SSL errors:**
```bash
# Update pip first
pip install --upgrade pip
```

## Contributing

When modifying scripts:

1. Test in dry-run mode first
2. Test on multiple platforms
3. Maintain color consistency
4. Update version number
5. Update documentation (INSTALL.md)
6. Keep output concise and clear

## Quick Reference

### One-Line Commands

```bash
# Install
curl -fsSL https://get.hopx.ai/install.sh | bash

# Uninstall
curl -fsSL https://get.hopx.ai/uninstall.sh | bash
```

### Installation Modes

| Mode | Command | Use Case |
|------|---------|----------|
| **pip** | `--mode pip` | Default, standard install |
| **pipx** | `--mode pipx` | Isolated environment |
| **git** | `--mode git` | Development/latest |

### Platform Support

| Platform | Supported | Package Manager |
|----------|-----------|-----------------|
| Ubuntu/Debian | Yes | apt-get |
| RHEL/CentOS | Yes | yum |
| Arch Linux | Yes | pacman |
| macOS | Yes | Homebrew |
| Windows | WSL only | - |

### Post-Install Verification

```bash
hopx --version
hopx --help
hopx run "print('Hello from Hopx!')"
```

## Resources

- Main documentation: [INSTALL.md](../INSTALL.md)
- CLI documentation: [README.md](../README.md)
- Support: support@hopx.ai
- Discord: https://discord.gg/hopx
