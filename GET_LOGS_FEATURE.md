# New Feature: `get_logs()` Method on BuildResult

## Overview

I've added a convenient method to retrieve logs directly from the `BuildResult` object returned after building a template.

## Usage

### Python SDK

```python
from hopx_ai import Template
from hopx_ai.template import BuildOptions

# Build template
result = await Template.build(template, BuildOptions(...))

# Get logs directly from result
logs = await result.get_logs()
print(logs.logs)

# Poll for new logs with offset
while not logs.complete:
    logs = await result.get_logs(offset=logs.offset)
    if logs.logs:
        print(logs.logs, end='')
    await asyncio.sleep(2)
```

**Full Example:** `python/examples/template_build_with_logs.py`

```bash
export HOPX_API_KEY="your_key"
python examples/template_build_with_logs.py
```

### JavaScript SDK

```typescript
import { Template } from '@hopx-ai/sdk';

// Build template
const result = await Template.build(template, options);

// Get logs directly from result
const logs = await result.getLogs();
console.log(logs.logs);

// Poll for new logs with offset
while (!logs.complete) {
  const logs = await result.getLogs(logs.offset);
  if (logs.logs) {
    process.stdout.write(logs.logs);
  }
  await new Promise(resolve => setTimeout(resolve, 2000));
}
```

**Full Example:** `javascript/examples/template-build-with-logs.ts`

```bash
export HOPX_API_KEY="your_key"
npm run build
npx tsx examples/template-build-with-logs.ts
```

## API

### Python: `BuildResult.get_logs(offset: int = 0) -> LogsResponse`

**Parameters:**
- `offset` (int, optional): Starting offset for log retrieval. Default: 0

**Returns:**
- `LogsResponse` object with:
  - `logs` (str): Log content
  - `offset` (int): New offset for next poll
  - `status` (str): Build status ('building', 'active', 'failed')
  - `complete` (bool): Whether build is complete
  - `request_id` (str, optional): Request ID

**Example:**
```python
result = await Template.build(template, options)

# Get all logs from beginning
logs = await result.get_logs()

# Get new logs from offset
logs = await result.get_logs(offset=123)
```

### JavaScript: `BuildResult.getLogs(offset?: number) -> Promise<LogsResponse>`

**Parameters:**
- `offset` (number, optional): Starting offset for log retrieval. Default: 0

**Returns:**
- Promise resolving to `LogsResponse` object with:
  - `logs` (string): Log content
  - `offset` (number): New offset for next poll
  - `status` (string): Build status ('building', 'active', 'failed')
  - `complete` (boolean): Whether build is complete
  - `requestId` (string, optional): Request ID

**Example:**
```typescript
const result = await Template.build(template, options);

// Get all logs from beginning
const logs = await result.getLogs();

// Get new logs from offset
const logs = await result.getLogs(123);
```

## Benefits

1. **Convenience**: No need to manually call the logs API with build_id
2. **Type Safety**: Full TypeScript/type hints support
3. **Polling Support**: Easy to implement log polling with offset
4. **Error Handling**: Built-in error handling

## Implementation Details

### Python SDK Changes

- **File:** `hopx_ai/template/types.py`
  - Added `_base_url` and `_api_key` fields to `BuildResult`
  - Added `get_logs()` method

- **File:** `hopx_ai/template/build_flow.py`
  - Updated `BuildResult` creation to include `_base_url` and `_api_key`

### JavaScript SDK Changes

- **File:** `src/template/types.ts`
  - Added `getLogs` to `BuildResult` interface

- **File:** `src/template/build-flow.ts`
  - Added `getLogs` method to returned `BuildResult` object

## Testing

Both SDK tests (`test_template_building.py` and `test-template-building.ts`) already test the log retrieval functionality.

Run tests:
```bash
# Python
export HOPX_API_KEY="your_key"
python examples/test_template_building.py

# JavaScript
export HOPX_API_KEY="your_key"
npm run test:template-building
```

## Backward Compatibility

This is a **non-breaking change**. All existing code continues to work as before. The new method is an additional convenience feature.

