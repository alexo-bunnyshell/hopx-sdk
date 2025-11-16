#!/usr/bin/env npx tsx
/**
 * Basic Preview URL Usage
 *
 * This example demonstrates how to get preview URLs for services
 * running inside Hopx sandboxes.
 *
 * Before running:
 *   export HOPX_API_KEY="your_api_key_here"
 *
 * Run:
 *   npx tsx examples/preview-url-basic.ts
 */

import { Sandbox } from '../src/index.js';

async function main() {
  console.log('🌐 Preview URL Basic Usage\n');

  // Create sandbox
  const sandbox = await Sandbox.create({ template: 'code-interpreter' });
  console.log(`✅ Sandbox created: ${sandbox.sandboxId}`);

  // Get agent URL (default port 7777)
  const agentUrl = await sandbox.agentUrl;
  console.log(`📡 Agent URL: ${agentUrl}`);

  // Get preview URL for custom port
  const apiUrl = await sandbox.getPreviewUrl(3000);
  console.log(`🔗 API URL (port 3000): ${apiUrl}`);

  const webUrl = await sandbox.getPreviewUrl(8080);
  console.log(`🌐 Web URL (port 8080): ${webUrl}`);

  // Cleanup
  await sandbox.kill();
  console.log('\n✅ Done!');
}

main().catch(console.error);
