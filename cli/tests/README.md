# Hopx CLI E2E Test Suite

End-to-end testing for the Hopx CLI covering all major command groups.

## Quick Start

```bash
# Go to CLI directory
cd /home/ubuntu/bns/hopx-sdks/cli

# Activate virtual environment
source .venv/bin/activate

# Run E2E tests
python tests/e2e_comprehensive.py
```

## Test Suite Overview

**Test File**: `tests/e2e_comprehensive.py`
**Total Tests**: 29
**Coverage**: All major CLI command groups

### Command Groups Tested

1. **System** (1 test) - Health checks and system status
2. **Config** (2 tests) - Configuration management
3. **Sandbox** (5 tests) - Sandbox lifecycle operations
4. **Files** (5 tests) - File operations within sandboxes
5. **Cmd** (3 tests) - Shell command execution
6. **Run** (2 tests) - Code execution
7. **Env** (5 tests) - Environment variable management
8. **Template** (3 tests) - Template operations
9. **Error Handling** (3 tests) - Error scenarios

## Test Results

### Latest Run (2025-11-27)

```
Total tests: 29
Passed: 29 ✓
Failed: 0 ✗
Success rate: 100.0%
Total duration: 247.76s
```

### Breakdown by Category

| Category | Passed | Total | Status |
|----------|--------|-------|--------|
| System   | 1      | 1     | ✓      |
| Config   | 2      | 2     | ✓      |
| Sandbox  | 5      | 5     | ✓      |
| Files    | 5      | 5     | ✓      |
| Cmd      | 3      | 3     | ✓      |
| Run      | 2      | 2     | ✓      |
| Env      | 5      | 5     | ✓      |
| Template | 3      | 3     | ✓      |
| Error    | 3      | 3     | ✓      |

## Requirements

- **Python**: 3.12+
- **API Key**: Valid HOPX_API_KEY in `.env` file
- **Network**: Active internet connection
- **Dependencies**: All CLI dependencies installed

## Test Features

### What's Tested

- ✓ Command execution via subprocess
- ✓ Table and JSON output formats
- ✓ Error handling and edge cases
- ✓ Resource creation and cleanup
- ✓ Real API integration
- ✓ All major CLI workflows

### What's NOT Tested

- Interactive terminal commands
- Desktop automation (VNC, screenshots)
- OAuth/authentication flows
- WebSocket terminal sessions
- Long-running background processes

## Test Architecture

### Design Principles

1. **Subprocess-based**: Tests run actual CLI commands
2. **Format validation**: Verifies table and JSON outputs
3. **Resource cleanup**: Auto-cleanup of created resources
4. **Existing resources**: Uses existing sandboxes when possible
5. **Error scenarios**: Tests both success and failure paths

### Test Structure

```python
class CLITester:
    def run_command()      # Execute CLI commands
    def test_case()        # Decorator for individual tests
    def cleanup_sandboxes() # Clean up resources
    def print_summary()    # Print test results
```

## Output Formats

The test suite validates multiple output formats:

### Table Format (default)
```bash
hopx sandbox list
```

### JSON Format
```bash
hopx -o json sandbox list
```

### Plain Format
```bash
hopx -o plain config show
```

## Common Issues

### Issue: API Key Not Found
**Solution**: Create `.env` file with `HOPX_API_KEY="your_key"`

### Issue: Command Not Found
**Solution**: Activate the virtual environment first

### Issue: Tests Fail with "Unexpected error"
**Solution**: Check API key is valid and has proper permissions

### Issue: Sandbox Creation Fails
**Solution**: Tests use existing sandboxes; create at least one sandbox first

## Adding New Tests

To add tests for new commands:

1. Add test method to appropriate section in `e2e_comprehensive.py`
2. Use `@self.test_case()` decorator
3. Follow naming convention: `test_<category>_<action>`
4. Update test count in this README
5. Run full test suite to verify

Example:

```python
@self.test_case("Sandbox: pause")
def test_pause():
    stdout, _, _ = self.run_command([
        "sandbox", "pause", self.sandbox_id
    ])
    assert "paused" in stdout.lower()
test_pause()
```

## Continuous Integration

The test suite is designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
- name: Run E2E Tests
  run: |
    source .venv/bin/activate
    python tests/e2e_comprehensive.py
```

## Performance

- **Average test duration**: ~8.5 seconds per test
- **Total execution time**: ~4 minutes
- **Fastest test**: 5.6s (health check)
- **Slowest test**: 16.6s (template info)

## Maintenance

### Regular Updates

- Update tests when CLI syntax changes
- Add tests for new features
- Review and update assertions
- Monitor execution time trends

### Test Data

- Uses real API endpoints
- Creates minimal test resources
- Cleans up after execution
- Reuses existing sandboxes

## Troubleshooting

### Debug Individual Tests

Modify the test file to run specific tests:

```python
# Comment out unwanted test groups
# self.test_files_commands()
# self.test_cmd_commands()
self.test_run_commands()  # Only run this one
```

### Verbose Output

Add print statements in test methods:

```python
print(f"stdout: {stdout}")
print(f"stderr: {stderr}")
print(f"returncode: {returncode}")
```

### Save Test Output

```bash
python tests/e2e_comprehensive.py 2>&1 | tee test_output.log
```

## Documentation

- **Test Output**: `tests/e2e_test_output.log`
- **Test Script**: `tests/e2e_comprehensive.py`

## Support

For issues or questions:
- Check test output logs
- Verify API key and permissions
- Verify all dependencies are installed
