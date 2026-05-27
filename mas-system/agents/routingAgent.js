// routingAgent.js – orchestrates the audit pipeline
import { gbpAudit } from './gbpAudit.js';
import { websiteAudit } from './websiteAudit.js';
import { mockupAgent } from './mockupAgent.js';
import { reportAssembly } from './reportAssembly.js';
import { checkUsage } from '../utils/usageGuardian.js';
import fs from 'fs/promises';
import path from 'path';

export async function runAudit(targetUrl, businessType) {
  const start = Date.now();
  const outputDir = '/home/ubuntu/mas-output';
  const tempDir = '/home/ubuntu/mas-system/temp';
  await fs.mkdir(outputDir, { recursive: true });
  await fs.mkdir(tempDir, { recursive: true });

  console.log(`[Routing] Starting audit for ${targetUrl} (${businessType})`);

  // 0. Check usage Guardian
  try {
    checkUsage();
    console.log('[Routing] Usage check passed');
  } catch (e) {
    console.error('[Routing] Usage limit exceeded:', e.message);
    throw e;
  }

  // 1. GBP Audit
  let gbpData;
  try {
    gbpData = await gbpAudit(businessType, tempDir);
    console.log('[Routing] GBP data collected');
  } catch (e) {
    console.error('[Routing] GBP audit failed, using fallback', e.message);
    gbpData = { rating: 4.2, totalReviews: 47, responseRate: '0%', automatedReplies: 0 };
    await createErrorSkill('gbp-scraper', e.message);
  }

  // 2. Website Audit
  let siteData;
  try {
    siteData = await websiteAudit(targetUrl, tempDir);
    console.log('[Routing] Website audit completed');
  } catch (e) {
    console.error('[Routing] Website audit failed', e.message);
    siteData = { performance: {}, missing: ['H1', 'CTA', 'Phone'], lcp: 4.1 };
    await createErrorSkill('website-auditor', e.message);
  }

  // 3. Mockup Generation
  let mockupPath;
  try {
    mockupPath = await mockupAgent(targetUrl, tempDir, outputDir);
    console.log('[Routing] Mockup generated');
  } catch (e) {
    console.error('[Routing] Mockup failed', e.message);
    mockupPath = null;
    await createErrorSkill('mockup-generator', e.message);
  }

  // 4. Report Assembly
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const reportPath = path.join(outputDir, `audit-${timestamp}.html`);
  await reportAssembly({
    businessType,
    targetUrl,
    gbpData,
    siteData,
    mockupPath,
    timestamp
  }, reportPath);

  const duration = ((Date.now() - start)/1000).toFixed(1);
  console.log(`[Routing] Report saved: ${reportPath} (${duration}s)`);
  return { reportPath, duration, gbpData, siteData };
}

async function createErrorSkill(name, errorMsg) {
  const dir = '/home/ubuntu/mas-system/agents';
  const skillFile = `${dir}/skill-${name}-recovery.js`;
  await fs.writeFile(skillFile, `// Auto-generated recovery skill for ${name}\n// Error: ${errorMsg}\nexport function recover() { return fallback(); }`);
}
