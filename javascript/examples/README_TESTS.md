# Template Building Tests

## JavaScript/TypeScript SDK Test

The `test-template-building.ts` script tests the complete template building flow for the JavaScript SDK, matching all tests from `test-template-build.sh`.

### Prerequisites

```bash
cd javascript/

# Install dependencies
npm install

# Build the SDK
npm run build
```

### Running the Test

```bash
# Set your API key
export HOPX_API_KEY="your_api_key_here"

# Optional: Set custom API base URL
export HOPX_BASE_URL="http://localhost:8080"  # Default: https://api.hopx.dev

# Run the test with tsx
npx tsx examples/test-template-building.ts

# Or add to package.json scripts and run with npm
npm run test:template-building
```

### Add to package.json

Add this script to your `package.json`:

```json
{
  "scripts": {
    "test:template-building": "tsx examples/test-template-building.ts"
  }
}
```

### What Gets Tested

1. **Step 1**: File upload to R2
   - Creates test files (app.py, requirements.txt)
   - Gets presigned upload URL
   - Uploads tar.gz to R2

2. **Step 2a**: Minimal template build
   - Required fields only: name, cpu, memory, diskGB, from_image
   - Single RUN step

3. **Step 2b**: Full features template
   - Multiple RUN steps
   - ENV variables
   - WORKDIR
   - USER
   - System packages installation

4. **Step 2c**: Template with COPY step
   - Uses uploaded files from Step 1
   - Tests COPY step with filesHash

5. **Step 3**: Validation errors (negative tests)
   - Missing required fields
   - CPU/Memory out of range
   - Alpine image rejection
   - Duplicate template name
   - Update non-existent template

6. **Step 4**: Update existing template
   - Tests update=true flag

7. **Step 5**: Build status check
   - Polls template build status

8. **Step 6**: Build logs retrieval
   - Gets build logs with offset

9. **Step 7**: List templates
   - Lists all templates and finds test templates

### Test Output

The script uses color-coded output:
- 🟢 Green ✓ = Success
- 🔴 Red ✗ = Error
- 🟡 Yellow ⚠ = Warning
- 🔵 Blue ▶ = Step

### Cleanup

Test creates temporary files in `/tmp/hopx_test_template_id_*_js.txt` which are automatically cleaned up at the end.

### Example Output

```
╔════════════════════════════════════════════════════════════════╗
║     HOPX JavaScript SDK - Template Building Flow Test         ║
╚════════════════════════════════════════════════════════════════╝

API Base URL: https://api.hopx.dev
Test Template: test-js-1234567890

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Checking API Key
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ API Key is set: hopx_live_...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Step 1: Get Presigned Upload URL & Upload to R2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▶ Creating test tar.gz file
✓ Test file created: 256 bytes
✓ Files hash: abc123...
▶ Requesting presigned upload URL
✓ Upload link received
✓ Upload URL received
▶ Uploading file to R2...
✓ File uploaded to R2 successfully!

[... more tests ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Test Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Passed: 25
Failed: 0
Warnings: 2

✓ All tests completed successfully!
```

### Troubleshooting

**Error: "HOPX_API_KEY environment variable is not set"**
- Make sure to export HOPX_API_KEY before running

**Error: "Failed to get upload link"**
- Check if R2/S3 is configured in api-public
- Verify API key has proper permissions

**Error: "Module not found"**
- Run `npm install` and `npm run build` first
- Make sure you're in the javascript/ directory

**TypeScript errors**
- Install tsx: `npm install -g tsx`
- Or use: `npx tsx examples/test-template-building.ts`

**Warnings about cache hits**
- Files already uploaded to R2 - this is normal and expected

### Dependencies

The test requires:
- `tar` package for creating tar.gz archives
- Node.js built-in `crypto` for SHA256 hashing
- Node.js built-in `fs` and `os` for file operations

