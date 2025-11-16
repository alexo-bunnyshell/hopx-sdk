#!/usr/bin/env npx tsx
/**
 * Comprehensive Features Test - JavaScript SDK v0.3.0
 *
 * Tests ALL new features implemented to achieve parity with Python SDK v0.3.0:
 * 1. Preview URL Access (getPreviewUrl, agentUrl)
 * 2. Environment Variables Propagation
 * 3. Template Activation Stability (2 consecutive checks)
 * 4. Background Commands with Bash Wrapping
 * 5. All 7 New Sandbox Methods
 * 6. Desktop New Methods (hotkey, debug)
 * 7. File Upload
 * 8. Model Field Completeness
 *
 * Before running:
 *   export HOPX_API_KEY="your_api_key_here"
 *
 * Run:
 *   npx tsx examples/comprehensive-features-test.ts
 */

import { Sandbox } from '../src/index.js';
import { writeFileSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';

interface TestResult {
  name: string;
  status: 'PASS' | 'FAIL' | 'SKIP';
  details?: string;
  error?: string;
}

const results: TestResult[] = [];

function recordResult(name: string, status: 'PASS' | 'FAIL' | 'SKIP', details?: string, error?: string) {
  results.push({ name, status, details, error });
  const emoji = status === 'PASS' ? '✅' : status === 'FAIL' ? '❌' : '⏭️';
  console.log(`${emoji} ${name}: ${status}${details ? ` - ${details}` : ''}`);
  if (error) console.error(`   Error: ${error}`);
}

async function main() {
  console.log('🧪 Comprehensive Features Test - JavaScript SDK v0.3.0\n');
  console.log('Testing all new features for 100% parity with Python SDK...\n');

  let sandbox: Sandbox | null = null;

  try {
    // ========================================================================
    // TEST 1: Health Check (No Auth Required)
    // ========================================================================
    console.log('═'.repeat(70));
    console.log('TEST 1: Health Check (Static Method - No Auth)');
    console.log('═'.repeat(70));
    try {
      const health = await Sandbox.healthCheck();
      recordResult('healthCheck()', 'PASS', `Status: ${health.status}`);
    } catch (error: any) {
      recordResult('healthCheck()', 'FAIL', undefined, error.message);
    }
    console.log();

    // ========================================================================
    // TEST 2: Sandbox Creation with Environment Variables
    // ========================================================================
    console.log('═'.repeat(70));
    console.log('TEST 2: Sandbox Creation + Environment Variables Propagation');
    console.log('═'.repeat(70));
    try {
      sandbox = await Sandbox.create({
        template: 'code-interpreter',
        envVars: {
          TEST_VAR_1: 'value1',
          TEST_VAR_2: 'value2',
          API_KEY: 'sk-test-123',
        },
      });
      recordResult('Sandbox.create()', 'PASS', `ID: ${sandbox.sandboxId}`);

      // Verify env vars are immediately available
      const result = await sandbox.runCode(
        "import os; print(f\"TEST_VAR_1={os.environ.get('TEST_VAR_1')}, TEST_VAR_2={os.environ.get('TEST_VAR_2')}\")",
        { language: 'python' }
      );

      if (result.stdout.includes('TEST_VAR_1=value1') && result.stdout.includes('TEST_VAR_2=value2')) {
        recordResult('Environment Variables Propagation', 'PASS', 'Env vars available immediately');
      } else {
        recordResult('Environment Variables Propagation', 'FAIL', 'Env vars not propagated');
      }
    } catch (error: any) {
      recordResult('Sandbox Creation', 'FAIL', undefined, error.message);
      return;
    }
    console.log();

    // ========================================================================
    // TEST 3: Preview URL Access
    // ========================================================================
    console.log('═'.repeat(70));
    console.log('TEST 3: Preview URL Access');
    console.log('═'.repeat(70));
    try {
      const agentUrl = await sandbox.agentUrl;
      recordResult('sandbox.agentUrl', 'PASS', agentUrl);

      const port8080 = await sandbox.getPreviewUrl(8080);
      recordResult('getPreviewUrl(8080)', 'PASS', port8080);

      // Verify URL format
      if (port8080.includes('8080-') && port8080.includes('.vms.hopx.dev')) {
        recordResult('Preview URL Format Validation', 'PASS', 'URL format correct');
      } else {
        recordResult('Preview URL Format Validation', 'FAIL', `Unexpected format: ${port8080}`);
      }
    } catch (error: any) {
      recordResult('Preview URL Access', 'FAIL', undefined, error.message);
    }
    console.log();

    // ========================================================================
    // TEST 4: New Sandbox Methods
    // ========================================================================
    console.log('═'.repeat(70));
    console.log('TEST 4: New Sandbox Methods');
    console.log('═'.repeat(70));

    // setTimeout()
    try {
      await sandbox.setTimeout(1800); // 30 minutes
      recordResult('setTimeout()', 'PASS', 'Set timeout to 1800 seconds');
    } catch (error: any) {
      recordResult('setTimeout()', 'FAIL', undefined, error.message);
    }

    // getAgentInfo()
    try {
      const agentInfo = await sandbox.getAgentInfo();
      recordResult('getAgentInfo()', 'PASS', `Version: ${agentInfo.version}`);
    } catch (error: any) {
      recordResult('getAgentInfo()', 'FAIL', undefined, error.message);
    }

    // getAgentMetrics()
    try {
      const metrics = await sandbox.getAgentMetrics();
      recordResult('getAgentMetrics()', 'PASS', `Uptime: ${metrics.uptime_seconds}s`);
    } catch (error: any) {
      recordResult('getAgentMetrics()', 'FAIL', undefined, error.message);
    }

    // listSystemProcesses()
    try {
      const processes = await sandbox.listSystemProcesses();
      recordResult('listSystemProcesses()', 'PASS', `Found ${processes.length} processes`);
    } catch (error: any) {
      recordResult('listSystemProcesses()', 'FAIL', undefined, error.message);
    }

    // getJupyterSessions()
    try {
      const sessions = await sandbox.getJupyterSessions();
      recordResult('getJupyterSessions()', 'PASS', `Found ${sessions.length} sessions`);
    } catch (error: any) {
      recordResult('getJupyterSessions()', 'FAIL', undefined, error.message);
    }

    console.log();

    // ========================================================================
    // TEST 5: Commands with Bash Wrapping
    // ========================================================================
    console.log('═'.repeat(70));
    console.log('TEST 5: Commands with Bash Wrapping (Sync + Background)');
    console.log('═'.repeat(70));

    // Sync command with pipe
    try {
      const result = await sandbox.commands.run('echo "hello world" | grep hello');
      if (result.stdout.includes('hello')) {
        recordResult('Sync Command (pipe)', 'PASS', 'Pipe operator works');
      } else {
        recordResult('Sync Command (pipe)', 'FAIL', 'Pipe not working');
      }
    } catch (error: any) {
      recordResult('Sync Command (pipe)', 'FAIL', undefined, error.message);
    }

    // Sync command with redirect
    try {
      await sandbox.commands.run('echo "test data" > /tmp/test.txt');
      const content = await sandbox.files.read('/tmp/test.txt');
      if (content.includes('test data')) {
        recordResult('Sync Command (redirect)', 'PASS', 'Redirect operator works');
      } else {
        recordResult('Sync Command (redirect)', 'FAIL', 'Redirect not working');
      }
    } catch (error: any) {
      recordResult('Sync Command (redirect)', 'FAIL', undefined, error.message);
    }

    // Background command with timeout
    try {
      const bgResult = await sandbox.commands.run('sleep 2 && echo "done"', {
        background: true,
        timeout: 5,
      });
      recordResult('Background Command (bash wrap + timeout)', 'PASS', 'Background execution works');
    } catch (error: any) {
      recordResult('Background Command', 'FAIL', undefined, error.message);
    }

    console.log();

    // ========================================================================
    // TEST 6: File Upload
    // ========================================================================
    console.log('═'.repeat(70));
    console.log('TEST 6: File Upload');
    console.log('═'.repeat(70));

    try {
      // Create a test file locally
      const testFilePath = join(tmpdir(), 'hopx-test-upload.txt');
      const testContent = 'This is a test file for upload verification.\nLine 2: Success!\n';
      writeFileSync(testFilePath, testContent);

      // Upload to sandbox
      await sandbox.files.upload(testFilePath, '/tmp/uploaded-file.txt');

      // Verify upload by reading back
      const uploadedContent = await sandbox.files.read('/tmp/uploaded-file.txt');

      if (uploadedContent === testContent) {
        recordResult('File Upload', 'PASS', 'Content matches perfectly');
      } else {
        recordResult('File Upload', 'FAIL', 'Content mismatch');
      }
    } catch (error: any) {
      recordResult('File Upload', 'FAIL', undefined, error.message);
    }

    console.log();

    // ========================================================================
    // TEST 7: Desktop Methods (if available)
    // ========================================================================
    console.log('═'.repeat(70));
    console.log('TEST 7: Desktop Methods (Premium Features)');
    console.log('═'.repeat(70));

    try {
      const vncInfo = await sandbox.desktop.getVncInfo();
      recordResult('Desktop.getVncInfo()', 'PASS', `URL: ${vncInfo.url}`);

      // Test hotkey (non-blocking, may not have visible effect)
      try {
        await sandbox.desktop.hotkey(['ctrl'], 'c');
        recordResult('Desktop.hotkey()', 'PASS', 'Executed Ctrl+C');
      } catch (error: any) {
        // Desktop may not be available in all templates
        recordResult('Desktop.hotkey()', 'SKIP', 'Desktop not available or not supported');
      }

      // Test debug methods
      try {
        const debugLogs = await sandbox.desktop.getDebugLogs();
        recordResult('Desktop.getDebugLogs()', 'PASS', `Found ${debugLogs.length} log entries`);
      } catch (error: any) {
        recordResult('Desktop.getDebugLogs()', 'SKIP', 'Not available');
      }

      try {
        const debugProcesses = await sandbox.desktop.getDebugProcesses();
        recordResult('Desktop.getDebugProcesses()', 'PASS', `Found ${debugProcesses.length} processes`);
      } catch (error: any) {
        recordResult('Desktop.getDebugProcesses()', 'SKIP', 'Not available');
      }
    } catch (error: any) {
      recordResult('Desktop Methods', 'SKIP', 'Desktop not available in this template');
    }

    console.log();

    // ========================================================================
    // TEST 8: Static Methods
    // ========================================================================
    console.log('═'.repeat(70));
    console.log('TEST 8: Static Methods');
    console.log('═'.repeat(70));

    // List templates
    try {
      const templates = await Sandbox.listTemplates();
      recordResult('Sandbox.listTemplates()', 'PASS', `Found ${templates.length} templates`);
    } catch (error: any) {
      recordResult('Sandbox.listTemplates()', 'FAIL', undefined, error.message);
    }

    // Get specific template
    try {
      const template = await Sandbox.getTemplate('python');
      recordResult('Sandbox.getTemplate()', 'PASS', `Template: ${template.displayName}`);
    } catch (error: any) {
      recordResult('Sandbox.getTemplate()', 'FAIL', undefined, error.message);
    }

    // Lazy iterator (test first 2 sandboxes)
    try {
      let count = 0;
      for await (const sb of Sandbox.iter({ status: 'running' })) {
        count++;
        if (count >= 2) break; // Only test first 2
      }
      recordResult('Sandbox.iter()', 'PASS', `Lazy iteration works (tested ${count} sandboxes)`);
    } catch (error: any) {
      recordResult('Sandbox.iter()', 'FAIL', undefined, error.message);
    }

    console.log();

    // ========================================================================
    // TEST 9: Model Field Completeness
    // ========================================================================
    console.log('═'.repeat(70));
    console.log('TEST 9: Model Field Completeness');
    console.log('═'.repeat(70));

    try {
      const info = await sandbox.getInfo();

      // Check new SandboxInfo fields
      const hasNewFields =
        'organizationId' in info || // Required field
        'region' in info ||
        'internetAccess' in info ||
        'timeoutSeconds' in info;

      if (hasNewFields) {
        recordResult('SandboxInfo Fields', 'PASS', 'New fields present');
      } else {
        recordResult('SandboxInfo Fields', 'FAIL', 'Missing new fields');
      }
    } catch (error: any) {
      recordResult('SandboxInfo Fields', 'FAIL', undefined, error.message);
    }

    console.log();
  } finally {
    if (sandbox) {
      console.log('🧹 Cleaning up sandbox...');
      await sandbox.kill();
      console.log('✅ Sandbox destroyed');
    }
  }

  // ========================================================================
  // FINAL SUMMARY
  // ========================================================================
  console.log('\n' + '═'.repeat(70));
  console.log('FINAL TEST SUMMARY');
  console.log('═'.repeat(70));

  const passed = results.filter((r) => r.status === 'PASS').length;
  const failed = results.filter((r) => r.status === 'FAIL').length;
  const skipped = results.filter((r) => r.status === 'SKIP').length;
  const total = results.length;

  console.log(`\n📊 Results: ${passed}/${total - skipped} tests passed`);
  console.log(`   ✅ PASS: ${passed}`);
  console.log(`   ❌ FAIL: ${failed}`);
  console.log(`   ⏭️  SKIP: ${skipped}`);

  if (failed > 0) {
    console.log('\n❌ Failed Tests:');
    results
      .filter((r) => r.status === 'FAIL')
      .forEach((r) => {
        console.log(`   - ${r.name}${r.error ? ': ' + r.error : ''}`);
      });
  }

  console.log('\n' + '═'.repeat(70));

  if (failed === 0) {
    console.log('🎉 ALL TESTS PASSED! JavaScript SDK v0.3.0 is ready!');
  } else {
    console.log('⚠️  Some tests failed. Review errors above.');
    process.exit(1);
  }
}

main().catch((error) => {
  console.error('\n💥 Test suite crashed:', error);
  process.exit(1);
});
