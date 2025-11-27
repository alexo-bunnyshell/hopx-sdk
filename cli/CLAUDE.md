# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Workflow Requirements

**CRITICAL: Always Test Changes and Provide Evidence**

When making any code changes:
1. **Write tests** that verify the fix/feature works correctly
2. **Run the tests** and capture the full output
3. **Provide evidence** in the form of test output showing success
4. **Update documentation**:
   - README.md (customer-facing, no fluff, clear and concise)
   - CLAUDE.md (internal, detailed technical implementation notes)
   - CHANGELOG.md (version history with clear descriptions)
   - Version bumps in `pyproject.toml` and `src/hopx_cli/__init__.py`

**Documentation Standards**:
- README.md: Enterprise-quality, customer-focused, easy to follow, no unnecessary words
- CLAUDE.md: Complete technical details, implementation notes, internal behaviors
- Test evidence must be included for all significant changes

**Writing Guidelines for All Documentation**:

Apply these principles to all writing (documentation, comments, commit messages, changelogs):

1. **Conciseness**: Use clear, direct sentences. Remove unnecessary words.
2. **Clarity**: Write for a wide audience. Explain technical terms when needed.
3. **Objectivity**: Maintain neutral tone. Avoid subjective adjectives and adverbs.
4. **Customer Focus**: Explain why information matters. Show the benefit.
5. **No Buzzwords**: Avoid marketing language and vague terms that obscure meaning.
6. **Simplicity**: Use simple words. Avoid jargon when plain language works.
7. **Readability**: Use short sentences. Avoid complex sentence structures.
8. **Action-Oriented**: Use subject-verb-object structure. Make doers and actions clear.
9. **No Clutter**: Remove words that don't contribute to the main point.
10. **Professional Tone**: Be warm and human while maintaining professionalism.

**Examples**:
- Bad: "This amazing fix is super fast and works perfectly!"
- Good: "The fix reduces wait time from 15 seconds to 6 seconds."

- Bad: "We leverage cutting-edge technology to provide world-class solutions."
- Good: "The CLI polls template status every 3 seconds."

## Overview

This is the **Hopx CLI** - the official command-line interface for Hopx.ai's cloud sandbox service. The CLI provides terminal-based access to all Hopx features including sandbox management, code execution, file operations, and template building.

**Version**: 0.1.0
**Python Support**: 3.12+
**License**: MIT
**Framework**: Typer (built on Click)

## Development Commands

### Setup with uv (recommended)

```bash
cd cli

# Install all dependencies including dev tools
uv sync --all-extras

# Activate the virtual environment
source .venv/bin/activate

# Or run commands without activation
uv run hopx --version
```

### Setup with pip

```bash
cd cli

# Install package in development mode with dependencies
pip install -e .

# Install with dev dependencies (pytest, ruff, mypy, pre-commit)
pip install -e ".[dev]"
```

### Testing

```bash
# Run E2E test suite
export HOPX_API_KEY="your_api_key_here"
python tests/e2e_comprehensive.py

# Run specific command tests
hopx system health
hopx --version
```

### Code Quality

```bash
# Lint with ruff (line-length: 100, target: py312)
ruff check src/hopx_cli/

# Auto-fix linting issues
ruff check src/hopx_cli/ --fix

# Format code with ruff (line-length: 100)
ruff format src/hopx_cli/

# Type check with mypy (strict mode, target: py312)
mypy src/hopx_cli/

# Run pre-commit hooks
pre-commit run --all-files
```

## Architecture

### Command Groups (15 total)

| Command | Alias | Module | Description |
|---------|-------|--------|-------------|
| `init` | - | `commands/init.py` | First-run setup wizard |
| `auth` | - | `commands/auth.py` | Authentication management |
| `sandbox` | `sb` | `commands/sandbox.py` | Sandbox lifecycle |
| `run` | - | `commands/run.py` | Code execution |
| `files` | `f` | `commands/files.py` | File operations |
| `cmd` | - | `commands/cmd.py` | Shell commands |
| `env` | - | `commands/env.py` | Environment variables |
| `terminal` | `term` | `commands/terminal.py` | Interactive terminal |
| `template` | `tpl` | `commands/template.py` | Template management |
| `config` | - | `commands/config.py` | Configuration |
| `system` | - | `commands/system.py` | Health and metrics |
| `org` | - | `commands/org.py` | Organization settings |
| `profile` | - | `commands/profile.py` | User profile |
| `members` | - | `commands/members.py` | Organization members |
| `billing` | - | `commands/billing.py` | Billing info |
| `usage` | - | `commands/usage.py` | Usage statistics |

### Core Components

**1. Configuration (`core/config.py`)**
- `CLIConfig` class using Pydantic Settings
- Environment variable loading with `HOPX_` prefix
- YAML config file: `~/.hopx/config.yaml`
- Multi-profile support

**2. Context (`core/context.py`)**
- `CLIContext` class for runtime state
- `OutputFormat` enum: TABLE, JSON, PLAIN
- State management for command chains

**3. Error Handling (`core/errors.py`)**
- SDK error mapping to CLI errors
- Exit codes (0-7, 130)
- Rich error display with suggestions
- `@handle_errors` decorator for commands

**4. Async Helpers (`core/async_helpers.py`)**
- `@run_async` decorator for async commands
- `run_with_timeout()` for operation timeouts
- `gather_with_concurrency()` for parallel tasks

**5. SDK Integration (`core/sdk.py`)**
- Sandbox instance caching
- Client initialization
- JWT token management

### Authentication Module (`auth/`)

**Components:**

1. **CredentialStore** (`credentials.py`)
   - Primary: System keyring (Keychain/Credential Manager/Secret Service)
   - Fallback: `~/.hopx/credentials.yaml` with 0600 permissions
   - Multi-profile support

2. **OAuth Flow** (`oauth.py`)
   - Browser-based login via WorkOS
   - Local callback server on random port
   - 2-minute timeout with graceful handling
   - Providers: GoogleOAuth, GitHubOAuth

3. **TokenManager** (`token.py`)
   - Environment variable priority
   - Auto-refresh expiring tokens (5-minute window)
   - Authentication status reporting

4. **APIKeyManager** (`api_keys.py`)
   - List, create, revoke API keys
   - Requires OAuth authentication
   - Key format: `hopx_live_<keyId>.<secret>`

### Output System (`output/`)

**Formatters:**
- `TableFormatter` - Rich tables with borders
- `JsonFormatter` - Machine-readable JSON
- `PlainFormatter` - Minimal text output

**Utilities:**
- Progress bars and spinners (`progress.py`)
- User prompts and confirmations (`prompts.py`)
- Color management with `--no-color` support

## Important Implementation Details

### Exit Codes

| Code | Constant | Meaning |
|------|----------|---------|
| 0 | - | Success |
| 1 | `CLIError.exit_code` | General error |
| 2 | `ValidationError.exit_code` | Validation error |
| 3 | `AuthenticationError.exit_code` | Authentication error |
| 4 | `NotFoundError.exit_code` | Not found |
| 5 | `TimeoutError.exit_code` | Timeout |
| 6 | `NetworkError.exit_code` | Network error |
| 7 | `RateLimitError.exit_code` | Rate limit |
| 130 | - | Interrupted (Ctrl+C) |

### SDK Error Mapping

SDK errors are automatically mapped to CLI errors with appropriate exit codes:

```python
@handle_errors
def my_command():
    sandbox = Sandbox.create(template="python")
    # If this fails, error is caught, displayed, and exits with correct code
```

| SDK Error | CLI Error | Exit Code |
|-----------|-----------|-----------|
| `AuthenticationError` | `AuthenticationError` | 3 |
| `TokenExpiredError` | `AuthenticationError` | 3 |
| `NotFoundError` | `NotFoundError` | 4 |
| `TemplateNotFoundError` | `NotFoundError` | 4 |
| `TimeoutError` | `TimeoutError` | 5 |
| `NetworkError` | `NetworkError` | 6 |
| `RateLimitError` | `RateLimitError` | 7 |
| `ValidationError` | `ValidationError` | 2 |
| Others | `CLIError` | 1 |

### Configuration Loading

Configuration is loaded with this precedence (highest to lowest):
1. CLI flags (`--api-key`, `--profile`)
2. Environment variables (`HOPX_API_KEY`, `HOPX_PROFILE`)
3. Config file (`~/.hopx/config.yaml`)
4. Default values

**Environment Variables:**
- `HOPX_API_KEY` - API key for authentication
- `HOPX_BASE_URL` - API base URL (default: https://api.hopx.dev)
- `HOPX_DEFAULT_TEMPLATE` - Default template name
- `HOPX_DEFAULT_TIMEOUT` - Default timeout in seconds
- `HOPX_OUTPUT_FORMAT` - Default output format (table/json/plain)
- `HOPX_PROFILE` - Configuration profile name

### Sandbox Caching

Sandbox instances are cached by API key and sandbox ID:

```python
_sandbox_cache = {
    "api_key_1:sb_123": <Sandbox instance>,
    "api_key_1:sb_456": <Sandbox instance>,
}
```

This prevents creating multiple connections to the same sandbox.

### Async/Sync Bridge

The CLI uses synchronous commands but the SDK supports async. The `@run_async` decorator handles this:

```python
from hopx_cli.core import run_async

@run_async
async def my_async_command():
    sandbox = await AsyncSandbox.create(template="python")
    result = await sandbox.run_code("print('Hello')")
    print(result.stdout)
```

## File Organization

```
cli/
├── src/hopx_cli/
│   ├── __init__.py              # Version and package info
│   ├── main.py                  # Typer app and command routing
│   ├── auth/                    # Authentication module
│   │   ├── __init__.py
│   │   ├── credentials.py       # Credential storage
│   │   ├── oauth.py             # OAuth browser flow
│   │   ├── token.py             # Token management
│   │   ├── api_keys.py          # API key management
│   │   └── display.py           # Auth display utilities
│   ├── commands/                # CLI commands
│   │   ├── auth.py              # hopx auth *
│   │   ├── sandbox.py           # hopx sandbox *
│   │   ├── run.py               # hopx run
│   │   ├── files.py             # hopx files *
│   │   ├── cmd.py               # hopx cmd *
│   │   ├── env.py               # hopx env *
│   │   ├── terminal.py          # hopx terminal *
│   │   ├── template.py          # hopx template *
│   │   ├── config.py            # hopx config *
│   │   ├── system.py            # hopx system *
│   │   ├── init.py              # hopx init
│   │   ├── org.py               # hopx org *
│   │   ├── profile.py           # hopx profile *
│   │   ├── members.py           # hopx members *
│   │   ├── billing.py           # hopx billing *
│   │   └── usage.py             # hopx usage *
│   ├── core/                    # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   ├── context.py           # CLI context and state
│   │   ├── errors.py            # Error handling
│   │   ├── async_helpers.py     # Async utilities
│   │   └── sdk.py               # SDK client management
│   ├── output/                  # Output formatting
│   │   ├── __init__.py
│   │   ├── formatters.py        # Format selection
│   │   ├── json_formatter.py    # JSON output
│   │   ├── plain_formatter.py   # Plain text output
│   │   ├── tables.py            # Rich tables
│   │   ├── progress.py          # Progress bars
│   │   └── prompts.py           # User prompts
│   └── utils/                   # Shared utilities
├── tests/
│   ├── e2e_comprehensive.py     # 29 E2E tests
│   └── README.md                # Test documentation
├── scripts/
│   ├── install.sh               # One-line installer
│   ├── uninstall.sh             # Uninstaller
│   └── README.md                # Script documentation
├── examples/                    # Example scripts
├── pyproject.toml               # Project metadata
├── README.md                    # Customer-facing docs
├── INSTALL.md                   # Installation guide
├── CHANGELOG.md                 # Version history
└── CLAUDE.md                    # This file
```

## Testing Strategy

### E2E Tests (`tests/e2e_comprehensive.py`)

29 tests covering:
- System health checks
- Configuration management
- Sandbox lifecycle (create, list, pause, resume, kill)
- File operations (write, read, list, delete)
- Command execution
- Code execution (Python, JavaScript, Bash)
- Environment variables
- Template operations
- Error handling

**Run tests:**
```bash
export HOPX_API_KEY="your_api_key"
python tests/e2e_comprehensive.py
```

**Test output format validation:**
- Table format verification
- JSON format parsing
- Exit code verification

### Unit Tests

Individual command modules have inline tests in `tests/` directory.

## Common Patterns

### Creating Commands

```python
import typer
from hopx_cli.core import handle_errors, CLIContext

app = typer.Typer()

@app.command("create")
@handle_errors
def create_sandbox(
    ctx: typer.Context,
    template: str = typer.Option("code-interpreter", "-t", "--template"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    """Create a new sandbox."""
    cli_ctx: CLIContext = ctx.obj

    # Use SDK
    sandbox = Sandbox.create(template=template, api_key=cli_ctx.config.get_api_key())

    # Output based on format
    if cli_ctx.is_json_output():
        print(json.dumps({"sandbox_id": sandbox.sandbox_id}))
    else:
        print(f"Created sandbox: {sandbox.sandbox_id}")
```

### Error Handling in Commands

```python
from hopx_cli.core import handle_errors, CLIError

@handle_errors
def my_command():
    # SDK errors automatically caught and mapped
    sandbox = Sandbox.create(template="nonexistent")  # Will raise NotFoundError

    # Custom CLI errors
    if not valid_input:
        raise CLIError("Invalid input", suggestion="Check --help for usage")
```

### Output Formatting

```python
from hopx_cli.output import format_table, format_json

def list_sandboxes(ctx: CLIContext):
    sandboxes = sandbox.list()

    if ctx.is_json_output():
        print(format_json([s.dict() for s in sandboxes]))
    elif ctx.is_table_output():
        print(format_table(
            sandboxes,
            columns=["id", "status", "template"],
            title="Sandboxes"
        ))
    else:
        for s in sandboxes:
            print(f"{s.id} {s.status}")
```

## Dependencies

**Core:**
- `hopx-ai>=0.3.8` - Official Python SDK
- `typer[all]>=0.12.0` - CLI framework
- `rich>=13.0.0` - Terminal formatting
- `pydantic>=2.0.0` - Configuration models
- `pydantic-settings>=2.0.0` - Environment variable loading
- `httpx>=0.25.0` - HTTP client
- `keyring>=24.0.0` - Secure credential storage
- `pyyaml>=6.0.0` - YAML config files
- `click>=8.0.0` - Typer dependency
- `pyperclip>=1.8.0` - Clipboard operations
- `qrcode>=7.4.0` - QR code generation

**Development:**
- `pytest>=8.0.0` - Testing framework
- `pytest-asyncio>=0.23.0` - Async test support
- `black>=24.0.0` - Code formatting
- `ruff>=0.3.0` - Linting
- `mypy>=1.8.0` - Type checking

## Security

- **Keyring encryption**: OS-level encryption for stored credentials
- **File permissions**: Config files restricted to 0600 (owner only)
- **Token refresh**: Auto-refresh tokens before expiration
- **API key masking**: Keys masked in status displays
- **HTTPS only**: All API communication over TLS
- **Never commit**: API keys, .env files, credentials.yaml

## Resources

- Website: https://hopx.ai
- Documentation: https://docs.hopx.ai/cli
- Dashboard: https://hopx.ai/dashboard
- Discord: https://discord.gg/hopx
- GitHub: https://github.com/hopx-ai/hopx-sdks
- Support: support@hopx.ai
