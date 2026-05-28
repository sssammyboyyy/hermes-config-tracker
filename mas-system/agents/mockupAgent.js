// mockupAgent.js – screenshot + OpenRouter Vision -> protected HTML
import puppeteer from 'puppeteer';
import fs from 'fs/promises';
import path from 'path';

// Use dynamic import for node-fetch (ESM compatibility)
let fetch;
try {
  fetch = (await import('node-fetch')).default;
} catch (_) {
  fetch = globalThis.fetch;
}

export async function mockupAgent(url, tempDir, outputDir) {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  await page.goto(url, { waitUntil: 'networkidle2' });
  const screenshotPath = path.join(tempDir, 'screenshot.png');
  await page.screenshot({ path: screenshotPath, fullPage: true });
  await browser.close();

  const imageBuffer = await fs.readFile(screenshotPath);
  const base64 = imageBuffer.toString('base64');

  const apiKey = process.env.OPENROUTER_API_KEY;
  const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
      'HTTP-Referer': 'http://localhost',
      'X-Title': 'MAS Mockup Agent'
    },
    body: JSON.stringify({
      model: 'google/gemini-2.0-flash-001', // free
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'text',
              text: 'Generate a single self-contained HTML file that visually mimics the website in the attached screenshot. ' +
                    'The HTML must include these protection layers: CSS watermark (text "ReviewTap x JCE Media" tiled), ' +
                    'right-click disabled, Ctrl+S/U/P and F12 blocked, DevTools detection with debugger loop, ' +
                    'a hidden canvas that scrambles pixels every frame, and a transparent overlay covering the whole page. ' +
                    'Return ONLY the raw HTML code, no explanation.'
            },
            {
              type: 'image_url',
              image_url: { url: `data:image/png;base64,${base64}` }
            }
          ]
        }
      ],
      max_tokens: 4096
    })
  });

  if (!response.ok) throw new Error(`OpenRouter error: ${response.status}`);
  const data = await response.json();
  const html = data.choices[0].message.content;
  // Extract HTML from potential markdown code fences
  const cleanHtml = html.replace(/```html|```/g, '').trim();

  const mockupPath = path.join(outputDir, 'mockup-protected.html');
  await fs.writeFile(mockupPath, cleanHtml);
  return mockupPath;
}
