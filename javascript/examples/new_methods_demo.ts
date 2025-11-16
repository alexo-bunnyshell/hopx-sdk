/**
 * Demo: All 7 New Methods in JavaScript SDK
 *
 * This example demonstrates all newly implemented methods from Python SDK v0.3.0
 */

import { Sandbox } from '../src/index.js';

async function main() {
  console.log('🚀 Demonstrating 7 New Methods\n');
  console.log('='.repeat(60));

  // 1. healthCheck() - Check API status (no auth required)
  console.log('\n1️⃣  Static Method: healthCheck()');
  console.log('-'.repeat(60));
  try {
    const health = await Sandbox.healthCheck();
    console.log('✅ API Health:', health);
  } catch (error: any) {
    console.log('❌ Health check failed:', error.message);
  }

  // 2. iter() - Lazy iterator for sandboxes
  console.log('\n2️⃣  Static Method: iter()');
  console.log('-'.repeat(60));
  console.log('Listing first 2 running sandboxes (lazy loading)...');
  let count = 0;
  for await (const sandbox of Sandbox.iter({ status: 'running' })) {
    count++;
    console.log(`  [${count}] Sandbox: ${sandbox.sandboxId}`);
    if (count >= 2) break;
  }
  if (count === 0) {
    console.log('  No running sandboxes found');
  }

  // 3. deleteTemplate() - Delete custom template
  console.log('\n3️⃣  Static Method: deleteTemplate()');
  console.log('-'.repeat(60));
  console.log('⚠️  Skipped (requires custom template ID)');
  console.log('   Usage: await Sandbox.deleteTemplate("template_123abc")');

  // Create a sandbox for instance method tests
  console.log('\n🔧 Creating test sandbox...');
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',
    timeoutSeconds: 600
  });
  console.log(`✅ Created sandbox: ${sandbox.sandboxId}`);

  try {
    // 4. setTimeout() - Update auto-kill timeout
    console.log('\n4️⃣  Instance Method: setTimeout()');
    console.log('-'.repeat(60));
    await sandbox.setTimeout(900); // 15 minutes
    console.log('✅ Timeout updated to 900 seconds');

    // 5. getAgentMetrics() - Get agent performance metrics
    console.log('\n5️⃣  Instance Method: getAgentMetrics()');
    console.log('-'.repeat(60));
    const metrics = await sandbox.getAgentMetrics();
    console.log('Agent Metrics:');
    console.log(`  Uptime: ${(metrics as any).uptime_seconds || 'N/A'} seconds`);
    console.log(`  Total Requests: ${(metrics as any).total_requests || 0}`);
    console.log(`  Total Errors: ${(metrics as any).total_errors || 0}`);

    // 6. listSystemProcesses() - List all system processes
    console.log('\n6️⃣  Instance Method: listSystemProcesses()');
    console.log('-'.repeat(60));
    const processes = await sandbox.listSystemProcesses();
    console.log(`Found ${processes.length} system processes`);
    if (processes.length > 0) {
      console.log('Sample processes:');
      processes.slice(0, 3).forEach(proc => {
        console.log(`  PID ${(proc as any).pid}: ${(proc as any).name || 'unknown'}`);
      });
    }

    // 7. getJupyterSessions() - Get Jupyter kernel sessions
    console.log('\n7️⃣  Instance Method: getJupyterSessions()');
    console.log('-'.repeat(60));
    const sessions = await sandbox.getJupyterSessions();
    console.log(`Found ${sessions.length} Jupyter sessions`);
    if (sessions.length > 0) {
      sessions.forEach((session: any, i: number) => {
        console.log(`  [${i + 1}] Kernel: ${session.kernel_id || 'N/A'}`);
        console.log(`      State: ${session.execution_state || 'N/A'}`);
      });
    } else {
      console.log('  (No active Jupyter sessions)');
    }

  } finally {
    // Cleanup
    console.log('\n🧹 Cleaning up...');
    await sandbox.kill();
    console.log('✅ Sandbox deleted');
  }

  console.log('\n' + '='.repeat(60));
  console.log('✅ All 7 methods demonstrated successfully!');
}

main().catch(error => {
  console.error('❌ Error:', error.message);
  process.exit(1);
});
