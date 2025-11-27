# Changelog

All notable changes to the Hopx CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-11-28

### Fixed

- Install script quick start now shows correct commands (`hopx init` as first step)
- Updated docs URL from docs.hopx.ai/cli to docs.hopx.dev
- Removed redundant INSTALL.md (quick start is in README)

## [0.1.0] - 2025-11-27

### Added

**Core Features**
- 15 command groups for complete sandbox management
- Browser-based OAuth authentication with Google and GitHub
- API key management (create, list, revoke)
- Multiple output formats: table, JSON, plain text
- Exit codes for scripting automation (0-7, 130)
- Configuration profiles for multiple environments
- Rich terminal output with progress bars and spinners

**Commands**
- `init` - First-run setup wizard with interactive configuration
- `auth` - Authentication management (login, logout, keys)
- `sandbox` (alias: `sb`) - Create, list, pause, resume, kill sandboxes
- `run` - Execute code in Python, JavaScript, Bash, or Go
- `files` (alias: `f`) - Read, write, list, delete, upload, download files
- `cmd` - Run shell commands in sandboxes
- `env` - Manage environment variables
- `terminal` (alias: `term`) - Interactive WebSocket terminal sessions
- `template` (alias: `tpl`) - List and build custom templates
- `config` - Configuration management and profiles
- `system` - Health checks and system metrics
- `org` - Organization settings
- `profile` - User profile management
- `members` - Organization member management
- `billing` - Billing information
- `usage` - Usage statistics

**Global Options**
- `--api-key` - Override API key
- `--profile` - Select configuration profile
- `--output` / `-o` - Output format (table, json, plain)
- `--quiet` / `-q` - Suppress non-essential output
- `--verbose` / `-v` - Increase verbosity
- `--no-color` - Disable colored output
- `--version` - Show version

**Authentication**
- Secure credential storage via system keyring (Keychain, Credential Manager, Secret Service)
- Fallback to encrypted file storage (~/.hopx/credentials.yaml)
- OAuth token refresh with automatic expiration handling
- API key format validation (hopx_live_<keyId>.<secret>)

**Configuration**
- YAML configuration file (~/.hopx/config.yaml)
- Environment variable support (HOPX_* prefix)
- Multiple profile support for dev/prod environments
- Config precedence: CLI flags > environment > config file > defaults

**Installation**
- One-line installer script (curl | bash)
- pip and pipx installation support
- Platform detection (Linux, macOS, Windows/WSL)
- Post-install verification

### Documentation

- README.md with quick start guide and installation options
- Internal CLAUDE.md for development guidance
