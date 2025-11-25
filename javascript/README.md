# Hopx JavaScript/TypeScript SDK

[![npm version](https://img.shields.io/npm/v/@hopx-ai/sdk.svg)](https://www.npmjs.com/package/@hopx-ai/sdk)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0%2B-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

JavaScript and TypeScript client for [Hopx.ai](https://hopx.ai).

## What is Hopx?

Hopx provides isolated cloud sandboxes (lightweight VMs) that start in ~100ms. Use cases:

- Execute untrusted code safely
- Run integration tests in clean environments
- Process data with Python/Node.js/Go/etc.
- Build AI agents that execute code
- Automate browser tasks

Each sandbox includes:
- Root access to the VM
- Network access (configurable)
- Pre-installed language runtimes and tools
- Persistent filesystem during session
- Automatic cleanup after timeout

## Installation

```bash
npm install @hopx-ai/sdk
```

## Quick Start

```typescript
import { Sandbox } from '@hopx-ai/sdk';

const sandbox = await Sandbox.create({
  template: 'code-interpreter',
  apiKey: 'your-api-key'  // or set HOPX_API_KEY environment variable
});

const result = await sandbox.runCode(`
console.log('Node.js', process.version);
console.log('Hello from Hopx!');
`);

console.log(result.stdout);
await sandbox.kill();
```

Get your API key at [hopx.ai/dashboard](https://hopx.ai/dashboard).

## Code Execution

Execute code in Python, JavaScript, Bash, or other languages:

```typescript
// Python
const result = await sandbox.runCode("print('Hello')", {
  language: 'python'
});

// JavaScript
const result = await sandbox.runCode("console.log('Hello')", {
  language: 'javascript'
});

// Bash
const result = await sandbox.runCode("echo 'Hello')", {
  language: 'bash'
});
```

The `runCode` method returns `stdout`, `stderr`, `exitCode`, and `executionTime`.

## File Operations

Read, write, and manage files in the sandbox:

```typescript
// Write file
await sandbox.files.write('/app/config.json', '{"key": "value"}');

// Read file
const content = await sandbox.files.read('/app/config.json');

// Upload from local disk
await sandbox.files.upload('./local-file.txt', '/app/remote-file.txt');

// List directory
const files = await sandbox.files.list('/app/');
files.forEach(file => {
  console.log(`${file.name}: ${file.size} bytes`);
});

// Delete file
await sandbox.files.remove('/app/temp.txt');
```

File upload uses multipart form data to transfer files from your local filesystem to the sandbox.

## Shell Commands

Execute shell commands with pipes, redirects, and environment variables:

```typescript
// Basic command
const result = await sandbox.commands.run('ls -la /app');
console.log(result.stdout);

// Command with pipe
await sandbox.commands.run('ls | grep test');

// Command with redirect
await sandbox.commands.run('echo "data" > output.txt');

// Background execution
await sandbox.commands.run('sleep 10 && echo done', {
  background: true,
  timeout: 30
});
```

Commands run in bash, allowing you to use shell features.

## Timeout Configuration

Default timeouts:
- Sync commands: 30 seconds
- Background commands: 120 seconds
- Code execution (`runCode`): 120 seconds

Set custom timeouts for long-running operations:

```typescript
// Package installation (5 minutes)
await sandbox.commands.run('npm install', { timeout: 300 });

// Large build (10 minutes)
await sandbox.runCode(buildScript, { timeout: 600 });

// Quick check (10 seconds)
await sandbox.commands.run('ls', { timeout: 10 });
```

## Environment Variables

Set environment variables during sandbox creation or at runtime:

```typescript
// Set during creation
const sandbox = await Sandbox.create({
  template: 'code-interpreter',
  envVars: {
    DATABASE_URL: 'postgresql://localhost/db',
    API_KEY: 'sk-prod-xyz'
  }
});

// Variables are available immediately
const result = await sandbox.runCode("import os; print(os.environ['API_KEY'])");

// Update at runtime
await sandbox.env.set('CACHE_ENABLED', 'true');
await sandbox.env.update({ LOG_LEVEL: 'info' });

// Read variables
const value = await sandbox.env.get('API_KEY');
const allVars = await sandbox.env.getAll();

// Delete variable
await sandbox.env.delete('DEBUG');
```

Environment variables persist across all code executions in the sandbox.

## Preview URLs

Access services running in your sandbox via public URLs:

```typescript
const sandbox = await Sandbox.create({ template: 'code-interpreter' });

// Get URL for service on port 8080
const appUrl = await sandbox.getPreviewUrl(8080);
// Returns: https://8080-{sandbox-id}.{region}.vms.hopx.dev/

// Get agent URL (port 7777)
const agentUrl = await sandbox.agentUrl;
```

This allows you to access web servers, APIs, or other services running inside the sandbox from external clients.

## Templates

Hopx provides public templates for code execution:

- `code-interpreter` - Python with pandas, numpy, matplotlib, and data science tools
- `base` - Minimal Ubuntu environment for custom builds

Or build custom templates:

```typescript
import { Template, waitForPort } from '@hopx-ai/sdk';

const template = new Template()
  .fromNodeImage('20')
  .copy('package.json', '/app/package.json')
  .copy('src/', '/app/src/')
  .runCmd('cd /app && npm install')
  .setWorkdir('/app')
  .setStartCmd('node src/index.js', waitForPort(3000));

const result = await Template.build(template, {
  name: 'my-app',
  apiKey: 'your-api-key'
});

const sandbox = await Sandbox.create({ templateId: result.templateID });
```

Templates create reusable sandbox configurations. The build process validates the template is ready before returning.

## Additional Methods

Manage sandboxes and monitor system state:

```typescript
// Iterate sandboxes (fetches pages as needed)
for await (const sandbox of Sandbox.iter({ status: 'running' })) {
  console.log(sandbox.sandboxId);
}

// Check API status (no authentication required)
const health = await Sandbox.healthCheck();

// Extend sandbox lifetime
await sandbox.setTimeout(3600);

// Get agent performance data
const metrics = await sandbox.getAgentMetrics();
console.log(`Uptime: ${metrics.uptime_seconds} seconds`);

// List running processes
const processes = await sandbox.listSystemProcesses();

// Get Jupyter kernel status
const sessions = await sandbox.getJupyterSessions();

// Delete custom template
await Sandbox.deleteTemplate('template_abc123');
```

## Desktop Automation

Control graphical applications (requires VNC-enabled templates):

```typescript
// Get VNC connection info
const vnc = await sandbox.desktop.getVncInfo();
console.log(`VNC URL: ${vnc.url}`);

// Capture screenshot
const screenshot = await sandbox.desktop.screenshot();

// Control mouse and keyboard
await sandbox.desktop.mouseClick(100, 200);
await sandbox.desktop.keyboardType('Hello, World!');
await sandbox.desktop.hotkey(['ctrl'], 'c');

// Manage windows
await sandbox.desktop.minimizeWindow(windowId);
await sandbox.desktop.focusWindow(windowId);

// Get debug logs
const logs = await sandbox.desktop.getDebugLogs();
```

Desktop automation requires templates with desktop environments installed.

## Rich Output Capture

Capture charts and visualizations from code execution:

```typescript
const result = await sandbox.runCode(`
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [1, 4, 9])
plt.show()
`, { language: 'python' });

// Access PNG image data
if (result.richOutputs && result.richOutputs.length > 0) {
  const pngData = result.richOutputs[0].data;  // Base64-encoded PNG
  const buffer = Buffer.from(pngData, 'base64');
  // Save or display the image
}
```

The SDK captures matplotlib/seaborn charts, HTML tables, and JSON output.

## Error Handling

Handle API errors and execution failures:

```typescript
import {
  HopxError,
  AuthenticationError,
  CodeExecutionError,
  SandboxExpiredError,
  TokenExpiredError
} from '@hopx-ai/sdk';

try {
  const sandbox = await Sandbox.create({ template: 'code-interpreter' });
  const result = await sandbox.runCode('1/0');
} catch (error) {
  if (error instanceof SandboxExpiredError) {
    console.error(`Sandbox expired: ${error.sandboxId}`);
    console.error(`Created: ${error.createdAt}, Expired: ${error.expiresAt}`);
  } else if (error instanceof TokenExpiredError) {
    console.error('JWT token expired, refresh required');
  } else if (error instanceof AuthenticationError) {
    console.error('Invalid API key');
  } else if (error instanceof CodeExecutionError) {
    console.error(`Execution failed: ${error.message}`);
  } else if (error instanceof HopxError) {
    console.error(`API error: ${error.message}, code: ${error.code}`);
  }
}
```

All errors include `requestId` for debugging and `code` for programmatic handling.

## Health Checks

Verify sandbox readiness before execution:

```typescript
// Simple check
const healthy = await sandbox.isHealthy();
if (!healthy) {
  console.error('Sandbox not ready');
}

// Preflight check before code execution
const result = await sandbox.runCode(longScript, {
  preflight: true,  // Throws if sandbox unhealthy or expired
  timeout: 300
});

// Detailed health verification (throws on failure)
await sandbox.ensureHealthy();
```

## Expiry Management

Monitor sandbox expiration to avoid unexpected failures:

```typescript
// Get time remaining
const seconds = await sandbox.getTimeToExpiry();
console.log(`${seconds} seconds until expiry`);

// Check if expiring soon (default: < 5 minutes)
const expiringSoon = await sandbox.isExpiringSoon();
const expiringIn10Min = await sandbox.isExpiringSoon(600);

// Get comprehensive expiry info
const info = await sandbox.getExpiryInfo();
console.log(`Expires: ${info.expiresAt}`);
console.log(`Time left: ${info.timeToExpiry}s`);
console.log(`Is expired: ${info.isExpired}`);

// Auto-monitor with callback
const sandbox = await Sandbox.create({
  template: 'code-interpreter',
  timeoutSeconds: 600,
  onExpiringSoon: (info) => {
    console.warn(`Sandbox expires in ${info.timeToExpiry}s!`);
  },
  expiryWarningThreshold: 120  // Warn 2 minutes before expiry
});

// Manual monitoring
sandbox.startExpiryMonitor(
  (info) => console.warn('Expiring soon!'),
  300,  // threshold: 5 minutes
  30    // check every 30 seconds
);

// Stop monitoring
sandbox.stopExpiryMonitor();
```

## TypeScript Support

The SDK includes full TypeScript type definitions:

```typescript
import {
  Sandbox,
  ExecutionResult,
  SandboxInfo,
  ExpiryInfo,
  ErrorCode,
  SandboxErrorMetadata
} from '@hopx-ai/sdk';

const sandbox = await Sandbox.create({ template: 'code-interpreter' });
const result: ExecutionResult = await sandbox.runCode("print('Hello')");
const info: SandboxInfo = await sandbox.getInfo();
const expiry: ExpiryInfo = await sandbox.getExpiryInfo();
```

## Cleanup

Call `kill()` to destroy the sandbox and stop billing:

```typescript
const sandbox = await Sandbox.create({ template: 'code-interpreter' });

try {
  await sandbox.runCode('console.log("Hello")');
} finally {
  await sandbox.kill();  // Always cleanup
}
```

Or set a timeout during creation:

```typescript
const sandbox = await Sandbox.create({
  template: 'code-interpreter',
  timeoutSeconds: 300  // Auto-kill after 5 minutes
});
```

## Troubleshooting

**Sandbox creation fails**: Verify your API key is valid and network connection is stable.

**Code execution fails**: Check `result.stderr` for error messages. Verify required packages are installed in the template.

**File not found**: Use absolute paths (`/app/file.txt`). Verify the file exists with `sandbox.files.list()`.

**TypeScript errors**: Install `@types/node` and update TypeScript to 4.9 or higher.

## Examples

See working examples in the `examples/` directory:

- `examples/preview-url-basic.ts` - Accessing services via public URLs
- `examples/env-vars-example.ts` - Environment variable management
- `examples/agent-commands.ts` - Shell command execution
- `examples/template-build.ts` - Building custom templates

## Links

- [Website](https://hopx.ai)
- [Documentation](https://docs.hopx.ai)
- [Dashboard](https://hopx.ai/dashboard)
- [GitHub](https://github.com/hopx-ai/hopx)
- [npm](https://www.npmjs.com/package/@hopx-ai/sdk)
- [Discord](https://discord.gg/hopx)

## Support

- Email: support@hopx.ai
- Discord: [discord.gg/hopx](https://discord.gg/hopx)
- GitHub Issues: [github.com/hopx-ai/hopx/issues](https://github.com/hopx-ai/hopx/issues)

## License

MIT - see [LICENSE](LICENSE) for details.
