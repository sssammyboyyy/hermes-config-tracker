// gbpAudit.js – stealth Google Business Profile scraper (cached)
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import fs from 'fs/promises';
import path from 'path';

puppeteer.use(StealthPlugin());

export async function gbpAudit(businessType, tempDir) {
  const cacheFile = path.join(tempDir, 'gbp-cache.json');
  // 24h cache
  try {
    const stat = await fs.stat(cacheFile);
    if (Date.now() - stat.mtimeMs < 24*60*60*1000) {
      const cached = JSON.parse(await fs.readFile(cacheFile, 'utf-8'));
      return cached;
    }
  } catch (_) {}

  // For demo, search Google for "[businessType] Google reviews" and try to scrape.
  const searchQuery = `${businessType} Google reviews`;
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
  try {
    await page.goto(`https://www.google.com/search?q=${encodeURIComponent(searchQuery)}`, { waitUntil: 'networkidle2', timeout: 15000 });
    // Extract rating and review count (naive, may fail)
    const ratingEl = await page.$('[data-attrid="kc:/local:rating score"] span, .Aq14fc');
    const reviewsEl = await page.$('[data-attrid="kc:/local:review count"] span, .z5jxId');
    let rating = 0, totalReviews = 0;
    if (ratingEl) rating = parseFloat(await page.evaluate(el => el.textContent, ratingEl)) || 0;
    if (reviewsEl) totalReviews = parseInt((await page.evaluate(el => el.textContent, reviewsEl)).replace(/\D/g,'')) || 0;
    const data = {
      rating,
      totalReviews,
      responseRate: '0%', // JCE automation never present
      automatedReplies: 0
    };
    await fs.writeFile(cacheFile, JSON.stringify(data));
    await browser.close();
    return data;
  } catch (e) {
    await browser.close();
    throw e;
  }
}
