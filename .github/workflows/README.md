# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the Hopx Python SDK.

## Workflows

### `test.yml` - Full Test Suite

Runs the complete test suite across multiple Python versions (3.8, 3.9, 3.10, 3.11, 3.12).

**Triggers:**
- Pull requests to `main`, `master`, or `develop`
- Pushes to `main`, `master`, or `develop`
- Only runs when Python files or workflow files change

**Features:**
- Tests on 5 Python versions in parallel
- Runs both integration and E2E tests
- Generates test reports and coverage
- Uploads artifacts for review
- Uploads coverage to Codecov (if configured)

### `test-quick.yml` - Quick PR Tests

Runs a quick test suite on Python 3.11 for faster PR feedback.

**Triggers:**
- Pull requests to `main`, `master`, or `develop`
- Only runs when Python files or workflow files change

**Features:**
- Fast feedback (single Python version)
- Runs integration tests
- Posts test results as PR comment
- Uploads test reports as artifacts

## Required Secrets

The following secrets must be configured in GitHub repository settings:

### Required
- `HOPX_API_KEY` - API key for running tests

### Optional
- `HOPX_TEST_BASE_URL` - Test API base URL (default: `https://api-eu.hopx.dev`)
- `HOPX_TEST_TEMPLATE` - Default template for tests (default: `code-interpreter`)

## Setting Up Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the required secrets listed above

## Workflow Behavior

### Test Execution
- Integration tests run first and must pass
- E2E tests run after integration tests (may be skipped if integration fails)
- E2E tests are set to `continue-on-error: true` to prevent blocking PRs due to flaky tests

### Artifacts
- Test reports are uploaded as artifacts for 7 days
- Coverage reports are generated and uploaded
- Reports can be downloaded from the Actions tab

### Notifications
- Quick test workflow posts results as PR comments
- Full test suite results are available in the Actions tab

## Customization

### Changing Python Versions

Edit the `matrix.python-version` in `test.yml`:

```yaml
matrix:
  python-version: ['3.10', '3.11', '3.12']  # Only test recent versions
```

### Skipping Tests

Add `[skip ci]` or `[ci skip]` to your commit message to skip CI runs.

### Running Specific Tests

Modify the `run_tests.sh` command in the workflow:

```yaml
run: |
  ./run_tests.sh -t integration -k "sandbox" -v
```

## Troubleshooting

### Tests are skipped
- Check that `HOPX_API_KEY` secret is set
- Verify the secret name matches exactly (case-sensitive)

### Tests fail with import errors
- Ensure `pip install -e .` completes successfully
- Check that all dependencies are listed in `pyproject.toml`

### Workflow doesn't trigger
- Check that file paths match the `paths` filter
- Verify the branch name matches the trigger branches
- Ensure the workflow file is in `.github/workflows/`

