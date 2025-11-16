#!/usr/bin/env npx tsx
/**
 * Agent Commands Example
 *
 * Demonstrates shell command execution with proper bash wrapping:
 * - Synchronous commands
 * - Background commands
 * - Commands with pipes, redirects, variables
 * - Environment variable support
 *
 * Before running:
 *   export HOPX_API_KEY="your_api_key_here"
 *
 * Run:
 *   npx tsx examples/agent-commands.ts
 */

import { Sandbox } from '../src/index.js';

async function main() {
  console.log('🔧 Agent Commands Example\n');

  const sandbox = await Sandbox.create({ template: 'code-interpreter' });
  console.log(`✅ Sandbox created: ${sandbox.sandboxId}\n`);

  try {
    // 1. Basic command execution
    console.log('1. Basic command execution:');
    const result1 = await sandbox.commands.run('pwd');
    console.log(`   Working directory: ${result1.stdout.trim()}`);
    console.log(`   Exit code: ${result1.exit_code}\n`);

    // 2. Command with pipe (requires bash wrapping)
    console.log('2. Command with pipe:');
    const result2 = await sandbox.commands.run('ls -la | grep python');
    console.log(`   Output: ${result2.stdout.trim()}`);
    console.log(`   ✅ Pipe operator works!\n`);

    // 3. Command with redirect (requires bash wrapping)
    console.log('3. Command with redirect:');
    await sandbox.commands.run('echo "test data" > /tmp/test.txt');
    const content = await sandbox.files.read('/tmp/test.txt');
    console.log(`   File content: ${content.trim()}`);
    console.log(`   ✅ Redirect operator works!\n`);

    // 4. Command with environment variables
    console.log('4. Command with environment variables:');
    const result3 = await sandbox.commands.run('echo "HOME=$HOME, USER=$USER"');
    console.log(`   Output: ${result3.stdout.trim()}`);
    console.log(`   ✅ Environment variables work!\n`);

    // 5. Command with custom env vars
    console.log('5. Command with custom env vars:');
    const result4 = await sandbox.commands.run('echo "CUSTOM=$CUSTOM_VAR"', {
      env: { CUSTOM_VAR: 'hello from env!' },
    });
    console.log(`   Output: ${result4.stdout.trim()}`);
    console.log(`   ✅ Custom env vars work!\n`);

    // 6. Background command
    console.log('6. Background command:');
    const bgResult = await sandbox.commands.run('sleep 2 && echo "background done"', {
      background: true,
      timeout: 10,
    });
    console.log(`   Process started: ${bgResult.stdout.trim()}`);
    console.log(`   ✅ Background command works!\n`);

    // 7. Command with working directory
    console.log('7. Command with working directory:');
    await sandbox.commands.run('mkdir -p /tmp/test_dir');
    const result5 = await sandbox.commands.run('pwd', { workingDir: '/tmp/test_dir' });
    console.log(`   Working directory: ${result5.stdout.trim()}`);
    console.log(`   ✅ Working directory works!\n`);

    // 8. Command with conditional (requires bash wrapping)
    console.log('8. Command with conditional:');
    const result6 = await sandbox.commands.run('[ -f /etc/passwd ] && echo "file exists" || echo "not found"');
    console.log(`   Output: ${result6.stdout.trim()}`);
    console.log(`   ✅ Conditional operators work!\n`);

    console.log('✅ All command features working correctly!');
    console.log('\n📝 All commands (sync AND background) are wrapped in `bash -c` for proper shell support.');
  } finally {
    await sandbox.kill();
    console.log('\n✅ Sandbox destroyed');
  }
}

main().catch(console.error);
