# Migration Guide

This guide helps you migrate your code when upgrading between major versions of the Hopx SDK.

## Table of Contents

- [Unreleased Changes](#unreleased-changes)

---

## Unreleased Changes

### Breaking Changes

#### 1. BuildOptions: `alias` renamed to `name`

The `alias` parameter in `BuildOptions` has been renamed to `name` for better clarity and consistency.

**JavaScript/TypeScript:**

```typescript
// ❌ Before
const result = await Template.build(template, {
  alias: 'my-python-app',
  apiKey: process.env.HOPX_API_KEY
});

// ✅ After
const result = await Template.build(template, {
  name: 'my-python-app',
  apiKey: process.env.HOPX_API_KEY
});
```

**Python:**

```python
# ❌ Before
result = await Template.build(
    template,
    BuildOptions(
        alias="my-python-app",
        api_key=os.environ["HOPX_API_KEY"]
    )
)

# ✅ After
result = await Template.build(
    template,
    BuildOptions(
        name="my-python-app",
        api_key=os.environ["HOPX_API_KEY"]
    )
)
```

---

#### 2. Template Base Image: FROM step removed

The `FROM` step type has been removed. Instead, base images are now specified:
- Via the `Template` constructor
- Via `from*Image()` methods

**JavaScript/TypeScript:**

```typescript
// ❌ Before - FROM as a step (never officially supported)
const template = new Template()
  .fromImage('python:3.11')
  .runCmd('pip install numpy');

// ✅ After - Base image in constructor or method
const template = new Template('python:3.11')
  .runCmd('pip install numpy');

// Or using helper methods
const template = new Template()
  .fromPythonImage('3.11')
  .runCmd('pip install numpy');
```

**Python:**

```python
# ❌ Before
template = Template().from_image('python:3.11').run_cmd('pip install numpy')

# ✅ After - Base image in constructor
template = Template(from_image='python:3.11').run_cmd('pip install numpy')

# Or using helper methods
template = Template().from_python_image('3.11').run_cmd('pip install numpy')
```

---

#### 3. Private Registry Authentication: Method naming clarification

Methods for private registry authentication have been renamed for clarity:

**JavaScript/TypeScript:**

```typescript
// ❌ Before
template.fromImage('registry.example.com/myimage:tag', {
  username: 'user',
  password: 'pass'
});

// ✅ After
template.fromPrivateImage('registry.example.com/myimage:tag', {
  username: 'user',
  password: 'pass'
});
```

**Python:**

```python
# ❌ Before
template.from_image('registry.example.com/myimage:tag', RegistryAuth(
    username='user',
    password='pass'
))

# ✅ After
template.from_private_image('registry.example.com/myimage:tag', RegistryAuth(
    username='user',
    password='pass'
))
```

The GCP and AWS registry methods have been renamed similarly:
- `fromGCPRegistry()` → `fromGCPPrivateImage()`
- `fromAWSRegistry()` → `fromAWSPrivateImage()`
- `from_gcp_registry()` → `from_gcp_private_image()`
- `from_aws_registry()` → `from_aws_private_image()`

---

### New Features

#### 1. BuildResult.getLogs() / BuildResult.get_logs()

You can now retrieve build logs directly from the `BuildResult` object:

**JavaScript/TypeScript:**

```typescript
const result = await Template.build(template, options);

// Get all logs
const logs = await result.getLogs();
console.log(logs.logs);

// Poll for new logs
let offset = 0;
while (!logs.complete) {
  const logs = await result.getLogs(offset);
  if (logs.logs) {
    process.stdout.write(logs.logs);
  }
  offset = logs.offset;
  await new Promise(resolve => setTimeout(resolve, 2000));
}
```

**Python:**

```python
result = await Template.build(template, options)

# Get all logs
logs = await result.get_logs()
print(logs.logs)

# Poll for new logs
offset = 0
while not logs.complete:
    logs = await result.get_logs(offset=offset)
    if logs.logs:
        print(logs.logs, end='')
    offset = logs.offset
    await asyncio.sleep(2)
```

---

#### 2. BuildOptions.update flag

You can now update existing templates by setting `update: true`:

**JavaScript/TypeScript:**

```typescript
// Create or update template
const result = await Template.build(template, {
  name: 'my-app',
  update: true,  // Will update if exists, create if not
  apiKey: process.env.HOPX_API_KEY
});
```

**Python:**

```python
# Create or update template
result = await Template.build(
    template,
    BuildOptions(
        name="my-app",
        update=True,  # Will update if exists, create if not
        api_key=os.environ["HOPX_API_KEY"]
    )
)
```

---

### Deprecations

#### StepType.FROM (TypeScript)

The `FROM` enum value in `StepType` is deprecated and will be removed in a future version. It is no longer used by the SDK.

---

## Need Help?

If you encounter issues during migration:

1. Check the [Documentation](https://docs.hopx.ai)
2. Join our [Discord Community](https://discord.gg/hopx)
3. Open an [Issue on GitHub](https://github.com/hopx-ai/hopx/issues)
4. Email us at support@hopx.ai

---

**Last Updated:** 2025-11-14

