// reportAssembly.js – fills report template
import fs from 'fs/promises';

const template = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Marketing Audit Report – {{businessType}}</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 800px; margin: auto; padding: 2rem; }
    .metric { background: #f4f4f4; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
    .highlight { color: #d93025; font-weight: bold; }
  </style>
</head>
<body>
  <h1>Marketing Audit & Strategy Report</h1>
  <p><strong>Business Type:</strong> {{businessType}} | <strong>Audited URL:</strong> {{targetUrl}}</p>
  <p><strong>Generated:</strong> {{timestamp}}</p>

  <h2>Google Business Profile Gap</h2>
  <div class="metric">
    <p>Rating: {{rating}}/5 ({{totalReviews}} reviews)</p>
    <p>Response Rate: <span class="highlight">{{responseRate}}</span></p>
    <p>Automated Replies: {{automatedReplies}} (0% smart routing)</p>
    <p><strong>Gap:</strong> You're collecting reviews but not leveraging them. JCE Media's AI delivers instant speed-to-lead,
    416% ROI, 65% lower CPL, 8.5× ROAS over $15M+ managed spend.</p>
  </div>

  <h2>Website Performance & UX</h2>
  <div class="metric">
    <p>FCP: {{fcp}}ms | LCP: {{lcp}}ms</p>
    <p>Missing Elements: {{missingElements}}</p>
    {{#slowLcp}}<p class="highlight">⚠ Slow LCP hurts rankings and conversions.</p>{{/slowLcp}}
  </div>

  <h2>Intelligence Gap – ReviewTap vs JCE Media</h2>
  <p>ReviewTap collects the reviews. JCE Media turns them into revenue: smart routing, instant lead alerts, full-funnel automation.</p>
  <p>Without it, you're leaving 4 out of 5 opportunities on the table.</p>

  {{#mockup}}
  <h2>Protected Mockup</h2>
  <iframe src="{{mockupFile}}" width="100%" height="500" style="border:1px solid #ccc;"></iframe>
  {{/mockup}}
</body>
</html>`;

export async function reportAssembly(data, outputPath) {
  const filled = template
    .replace('{{businessType}}', data.businessType)
    .replace('{{targetUrl}}', data.targetUrl)
    .replace('{{timestamp}}', data.timestamp)
    .replace('{{rating}}', data.gbpData.rating)
    .replace('{{totalReviews}}', data.gbpData.totalReviews)
    .replace('{{responseRate}}', data.gbpData.responseRate)
    .replace('{{automatedReplies}}', data.gbpData.automatedReplies)
    .replace('{{fcp}}', data.siteData.performance?.fcp || 0)
    .replace('{{lcp}}', data.siteData.performance?.lcp || 0)
    .replace('{{missingElements}}', data.siteData.missing.join(', ') || 'None')
    .replace('{{#slowLcp}}', (data.siteData.performance?.lcp > 2500 ? '' : '<!--'))
    .replace('{{/slowLcp}}', (data.siteData.performance?.lcp > 2500 ? '' : '-->'))
    .replace('{{#mockup}}', data.mockupPath ? '' : '<!--')
    .replace('{{/mockup}}', data.mockupPath ? '' : '-->')
    .replace('{{mockupFile}}', data.mockupPath ? './mockup-protected.html' : '');

  await fs.writeFile(outputPath, filled);
}
