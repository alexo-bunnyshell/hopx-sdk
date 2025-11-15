# Changelog

All notable changes to the Hopx SDKs will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.21] - 2025-15-11 - Python SDK
Implement complete OpenAPI specification (v2025-10-21) compliance with
  full endpoint coverage and enhanced models.

  New Endpoints:
  - Add DELETE /v1/templates/{templateID} for custom template deletion
  - Expose GET /health as public method (no auth required)

  Model Enhancements:
  - SandboxInfo: Add internet_access, live_mode, direct_url, preview_url,
    timeout_seconds, expires_at fields from OpenAPI spec
  - Template: Add is_public, build_id, organization_id, created_at,
    updated_at, object, request_id fields from OpenAPI spec

  Implementation Updates:
  - Enhanced get_info() parsing to include all OpenAPI response fields
  - Proper datetime parsing for created_at and expires_at timestamps
  - Backward compatibility maintained with legacy fields (started_at, end_at)
  - Both sync (Sandbox) and async (AsyncSandbox) implementations updated
  - All 18 Public API endpoints now fully implemented and tested

  OpenAPI Coverage:
  - System endpoints: 1/1 (health check)
  - Sandbox endpoints: 10/10 (full lifecycle management)
  - Template endpoints: 7/7 (complete CRUD + build operations)

## [0.1.21] - 2025-01-11 - JavaScript SDK
## [0.1.19] - 2025-01-11 - Python SDK

### 🎉 Initial Public Release

This is the first public release of the Hopx SDKs - a complete, production-ready toolkit for creating and managing cloud sandboxes.

### ✨ Features

**Core Capabilities:**
- ⚡ Sandbox creation in ~100ms
- 🐍 Python SDK (v0.1.19)
- 📦 JavaScript/TypeScript SDK (v0.1.21)
- 🔐 Secure VM isolation
- 🌍 Multi-language support (Python, Node.js, Go, Rust, Java)
- 📊 Rich output capture (PNG, HTML, JSON)
- 🗂️ Complete file operations
- 🖥️ Desktop automation (VNC, mouse, keyboard)
- 🔧 Custom template building
- 📡 WebSocket streaming

**SDK Features:**
- Sandbox Management (create, kill, info, list)
- Code Execution (multi-language, rich outputs)
- File Operations (read, write, delete, list)
- Command Execution (sync & async)
- Environment Variables
- Process Management
- Cache Management
- Template Building (Docker-like)
- Desktop Automation (Premium)

**Developer Experience:**
- 📚 Comprehensive documentation
- 📖 20+ cookbook examples
- 🔄 Async/await support
- 🎯 TypeScript definitions
- ⚠️ Rich error handling
- 🧪 Production-ready

### 📦 Installation

```bash
# Python
pip install hopx-ai

# JavaScript
npm install @hopx-ai/sdk
```

### 🔗 Links

- Python SDK: [PyPI](https://pypi.org/project/hopx-ai/)
- JavaScript SDK: [npm](https://www.npmjs.com/package/@hopx-ai/sdk)
- Documentation: [docs.hopx.ai](https://docs.hopx.ai)
- Website: [hopx.ai](https://hopx.ai)

### 📝 SDK-Specific Changelogs

For detailed version history:
- [Python CHANGELOG](python/CHANGELOG.md)
- [JavaScript CHANGELOG](javascript/CHANGELOG.md)

---

## Release Notes Format

This monorepo contains two SDKs with independent versioning:

- **Python SDK** (`hopx-ai` on PyPI) - See [python/CHANGELOG.md](python/CHANGELOG.md)
- **JavaScript SDK** (`@hopx-ai/sdk` on npm) - See [javascript/CHANGELOG.md](javascript/CHANGELOG.md)

Each SDK has its own release schedule and version numbers.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

