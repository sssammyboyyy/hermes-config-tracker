// websiteAudit.js – heuristic web audit using Puppeteer Performance API
import puppeteer from 'puppeteer';
import fs from 'fs/promises';
import path from 'path';

export async function websiteAudit(url, tempDir) {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 20000 });

  // Performance metrics
  const perf = await page.evaluate(() => {
    const nav = performance.getEntriesByType('navigation')[0];
    const paint = performance.getEntriesByType('paint');
    const fcp = paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0;
    return {
      fcp: Math.round(fcp),
      lcp: 0, // will get later
      tti: 0
    };
  });

  // LCP via PerformanceObserver (simplified)
  const lcp = await page.evaluate(() => {
    return new Promise(resolve => {
      let lcpVal = 0;
      const observer = new PerformanceObserver(list => {
        const entries = list.getEntries();
        const last = entries[entries.length-1];
        if (last) lcpVal = last.startTime;
      });
      observer.observe({type: 'largest-contentful-paint', buffered: true});
      setTimeout(() => {
        observer.disconnect();
        resolve(Math.round(lcpVal));
      }, 3000);
    });
  });
  perf.lcp = lcp;

  // Heuristic checks
  const missing = [];
  const h1 = await page.$('h1');
  if (!h1) missing.push('H1');
  const phone = await page.$('a[href^="tel:"], a[href^="callto:"]');
  const phoneText = await page.evaluate(() => document.body.innerText.match(/(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/));
  if (!phone && !phoneText) missing.push('Phone');
  const cta = await page.$('a[class*="cta"], button[class*="cta"]');
  if (!cta) missing.push('CTA');
  if (perf.lcp > 2500) missing.push('Slow LCP');

  await browser.close();
  return { performance: perf, missing };
}
