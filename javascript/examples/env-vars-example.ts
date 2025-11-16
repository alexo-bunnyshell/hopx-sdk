#!/usr/bin/env npx tsx
/**
 * Environment Variables Example
 *
 * Demonstrates environment variable management:
 * - Setting env vars during sandbox creation
 * - Setting/updating env vars after creation
 * - Getting individual and all env vars
 * - Per-request env var overrides
 * - Environment variable precedence
 *
 * Before running:
 *   export HOPX_API_KEY="your_api_key_here"
 *
 * Run:
 *   npx tsx examples/env-vars-example.ts
 */

import { Sandbox } from '../src/index.js';

async function main() {
  console.log('🚀 Environment Variables Example\n');

  // 1. Create sandbox with environment variables
  console.log('1. Creating sandbox with environment variables...');
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',
    envVars: {
      DATABASE_URL: 'postgresql://localhost:5432/mydb',
      API_KEY: 'sk-prod-abc123xyz',
      DEBUG: 'true',
      MAX_RETRIES: '3',
    },
  });
  console.log(`✅ Sandbox created: ${sandbox.sandboxId}\n`);

  try {
    // 2. Verify env vars are available in code execution
    console.log('2. Verifying environment variables...');
    const result1 = await sandbox.runCode(`
import os

print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
print(f"API_KEY: {os.environ.get('API_KEY')[:10]}...")  # Mask sensitive data
print(f"DEBUG: {os.environ.get('DEBUG')}")
print(f"MAX_RETRIES: {os.environ.get('MAX_RETRIES')}")
`, { language: 'python' });
    console.log(`   Output:\n${result1.stdout}`);

    // 3. Get individual environment variable
    console.log('3. Getting individual environment variable...');
    const debugValue = await sandbox.env.get('DEBUG');
    console.log(`   DEBUG = ${debugValue}\n`);

    // 4. Update environment variables
    console.log('4. Updating environment variables...');
    await sandbox.env.update({
      DEBUG: 'false',          // Change existing
      LOG_LEVEL: 'info',       // Add new
      CACHE_ENABLED: 'true',   // Add new
    });
    console.log('   ✅ Environment variables updated\n');

    // 5. Verify updates
    console.log('5. Verifying updates...');
    const result2 = await sandbox.runCode(`
import os

print(f"DEBUG (updated): {os.environ.get('DEBUG')}")
print(f"LOG_LEVEL (new): {os.environ.get('LOG_LEVEL')}")
print(f"CACHE_ENABLED (new): {os.environ.get('CACHE_ENABLED')}")
`, { language: 'python' });
    console.log(`   Output:\n${result2.stdout}`);

    // 6. Get all environment variables
    console.log('6. Getting all environment variables...');
    const allVars = await sandbox.env.getAll();
    console.log(`   Found ${Object.keys(allVars).length} environment variables`);
    console.log('   Custom variables:');
    const customVars = [
      'DATABASE_URL',
      'API_KEY',
      'DEBUG',
      'MAX_RETRIES',
      'LOG_LEVEL',
      'CACHE_ENABLED',
    ];
    for (const varName of customVars) {
      let value = allVars[varName] || 'NOT SET';
      // Mask sensitive values
      if (varName.includes('KEY') || varName.includes('SECRET') || varName.includes('PASSWORD')) {
        value = value !== 'NOT SET' ? '***MASKED***' : value;
      }
      console.log(`      ${varName}: ${value}`);
    }
    console.log();

    // 7. Per-request environment variable override
    console.log('7. Per-request environment variable override...');
    console.log('   Running code with request-specific env vars...');
    const result3 = await sandbox.runCode(`
import os

print(f"DEBUG (request override): {os.environ.get('DEBUG')}")
print(f"CUSTOM_VAR (request only): {os.environ.get('CUSTOM_VAR')}")
`, {
      language: 'python',
      env: { DEBUG: 'verbose', CUSTOM_VAR: 'request-specific' },
    });
    console.log(`   Output:\n${result3.stdout}`);

    // 8. Verify sandbox-level env is unchanged
    console.log('8. Verifying sandbox-level env is unchanged...');
    const result4 = await sandbox.runCode(
      "import os; print(f\"DEBUG: {os.environ.get('DEBUG')}\")",
      { language: 'python' }
    );
    console.log(`   Output: ${result4.stdout.trim()}\n`);

    // 9. Set individual environment variable
    console.log('9. Setting individual environment variable...');
    await sandbox.env.set('FEATURE_FLAG_NEW_UI', 'enabled');
    const result5 = await sandbox.runCode(
      'import os; print(os.environ.get("FEATURE_FLAG_NEW_UI"))',
      { language: 'python' }
    );
    console.log(`   FEATURE_FLAG_NEW_UI = ${result5.stdout.trim()}\n`);

    // 10. Delete environment variable
    console.log('10. Deleting environment variable...');
    await sandbox.env.delete('CACHE_ENABLED');
    const result6 = await sandbox.runCode(
      'import os; print(os.environ.get("CACHE_ENABLED", "NOT SET"))',
      { language: 'python' }
    );
    console.log(`   CACHE_ENABLED after deletion: ${result6.stdout.trim()}\n`);

    // 11. Environment variables in commands
    console.log('11. Environment variables in shell commands...');
    const cmdResult1 = await sandbox.commands.run('echo "DEBUG=$DEBUG, LOG_LEVEL=$LOG_LEVEL"');
    console.log(`   Command output: ${cmdResult1.stdout.trim()}\n`);

    // 12. Command with request-specific env
    console.log('12. Command with request-specific env override...');
    const cmdResult2 = await sandbox.commands.run('echo "TEMP_VAR=$TEMP_VAR"', {
      env: { TEMP_VAR: 'temporary-value' },
    });
    console.log(`   Command output: ${cmdResult2.stdout.trim()}\n`);

    console.log('✅ All environment variable operations completed successfully!');

    console.log('\n📝 Environment Variable Precedence (highest to lowest):');
    console.log('   1. Request-specific env (via runCode(..., { env: {...} }))');
    console.log('   2. Sandbox-level env (via sandbox.env.set/update)');
    console.log('   3. Creation-time env (via Sandbox.create({ envVars: {...} }))');
    console.log('   4. Template/system default env');
  } finally {
    // Cleanup
    console.log('\n🧹 Cleaning up...');
    await sandbox.kill();
    console.log('✅ Sandbox destroyed');
  }
}

main().catch(console.error);
