// multiAgentSystem.js – main entry point
import { runAudit } from './agents/routingAgent.js';
import { checkUsage } from './utils/usageGuardian.js';

const args = process.argv.slice(2);
if (args.length < 2) {
  console.log('Usage: node multiAgentSystem.js <url> <businessType>');
  process.exit(1);
}
const [url, businessType] = args;

// Check usage before starting
try {
  checkUsage();
} catch (e) {
  console.error('❌ Usage limit exceeded:', e.message);
  process.exit(1);
}

runAudit(url, businessType)
  .then(({ reportPath, duration }) => {
    console.log(`\n✅ Audit complete in ${duration}s`);
    console.log(`📄 Report: ${reportPath}`);
  })
  .catch(err => {
    console.error('❌ Fatal error:', err.message);
    process.exit(1);
  });
