/**
 * Template Building with Log Monitoring Example
 * 
 * Shows how to build a template and monitor its logs using the new getLogs() method.
 */

import { Template } from '../src/index.js';

async function main() {
  console.log('🚀 Building Template with Log Monitoring\n');
  
  // 1. Define template
  const template = new Template()
    .fromPythonImage('3.11-slim')
    .runCmd('apt-get update && apt-get install -y curl')
    .runCmd('pip install flask gunicorn')
    .setWorkdir('/app');
  
  // 2. Start building (without log callbacks for cleaner output)
  console.log('Starting build...');
  const result = await Template.build(template, {
    name: `example-template-${Date.now()}`,
    apiKey: process.env.HOPX_API_KEY || '',
    baseURL: process.env.HOPX_BASE_URL || 'https://api.hopx.dev',
    cpu: 2,
    memory: 2048,
    diskGB: 10,
  });
  
  console.log('✅ Build started!');
  console.log(`   Template ID: ${result.templateID}`);
  console.log(`   Build ID: ${result.buildID}`);
  console.log();
  
  // 3. Monitor logs using the new getLogs() method
  console.log('📋 Monitoring build logs...\n');
  
  let offset = 0;
  while (true) {
    // Get logs from current offset
    const logsResponse = await result.getLogs(offset);
    
    // Print new logs if any
    if (logsResponse.logs) {
      process.stdout.write(logsResponse.logs);
    }
    
    // Update offset for next iteration
    offset = logsResponse.offset;
    
    // Check if build is complete
    if (logsResponse.complete) {
      console.log('\n✅ Build complete!');
      console.log(`   Status: ${logsResponse.status}`);
      break;
    }
    
    // Wait before polling again
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  console.log();
  console.log(`🎉 Template ready to use: ${result.templateID}`);
  console.log(`   Build duration: ${result.duration}ms`);
}

main().catch(error => {
  console.error('❌ Error:', error.message);
  process.exit(1);
});

