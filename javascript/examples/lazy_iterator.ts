/**
 * Example: Using Sandbox.iter() for lazy loading
 *
 * Demonstrates the lazy iterator pattern for efficient sandbox listing.
 * Only fetches pages as needed, ideal for large result sets.
 */

import { Sandbox } from '../src/index.js';

async function main() {
  console.log('🔍 Lazy Loading Sandboxes...\n');

  let count = 0;
  let foundRunning = false;

  // Iterate through sandboxes lazily - only fetches pages as needed
  for await (const sandbox of Sandbox.iter({ status: 'running' })) {
    count++;
    console.log(`[${count}] Sandbox ID: ${sandbox.sandboxId}`);

    // Get detailed info
    const info = await sandbox.getInfo();
    console.log(`    Status: ${info.status}`);
    console.log(`    Template: ${info.templateName || info.templateId}`);
    console.log(`    Created: ${info.createdAt}`);
    console.log('');

    foundRunning = true;

    // Example: Stop iteration early (doesn't fetch remaining pages!)
    if (count >= 3) {
      console.log('✅ Found 3 running sandboxes, stopping early');
      break;
    }
  }

  if (!foundRunning) {
    console.log('No running sandboxes found');
  }

  console.log(`\n📊 Total sandboxes checked: ${count}`);
}

main().catch(console.error);
