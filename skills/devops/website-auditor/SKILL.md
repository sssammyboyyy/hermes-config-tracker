---
name: website-auditor
description: "Heuristic web performance and UX checker — extracts FCP, LCP, TTI via browser Performance API, checks for missing H1, CTA, phone number, and slow LCP."
version: 1.1.0
author: MAS Orchestrator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [mas, website, audit, performance, ux, lcp, fcp, seo]
    related_skills: [marketing-audit]
---

# Website Auditor — Performance & UX Checker

Audits a website for performance, UX, and conversion readiness. Uses browser Performance API when available, with curl-based fallback.

## Input

- `url` — the website to audit
- `temp_dir` — where to write `site-audit.json` (default: `/home/samuelj121314/mas-system/temp/`)

## Output

`site-audit.json` with structure:

```json
{
  "url": "https://example.com",
  "audited_at": "2026-05-26T12:00:00Z",
  "http_status": 200,
  "performance": {
    "dns_lookup_s": 0.331,
    "tcp_connect_s": 0.284,
    "tls_handshake_s": 0.842,
    "ttfb_s": 1.839,
    "total_load_s": 2.834,
    "page_size_kb": 99,
    "fcp_estimated_ms": 1839,
    "lcp_estimated_ms": 2834,
    "tti_estimated_ms": 3500,
    "external_resources": 23,
    "images": 9
  },
  "seo": {
    "has_h1": true,
    "h1_text": "Welcome to Example Hotel",
    "title": "Example Hotel — Book Now",
    "meta_description": "...",
    "has_schema_markup": false
  },
  "conversion": {
    "has_phone": true,
    "phone_numbers": ["+1-555-123-4567"],
    "has_cta": true,
    "cta_text": "Book Now",
    "has_contact_form": true,
    "has_live_chat": false
  },
  "gaps": [
    "TTFB is 1.84s (> 0.8s threshold) — server response is slow",
    "LCP is 2834ms (> 2.5s threshold) — losing 53% of mobile visitors"
  ]
}
```

## Method

### Primary: Browser Performance API

Use `browser_navigate` to load the site, then `browser_console` to extract Performance API data:

```javascript
const perf = performance.getEntriesByType('navigation')[0];
const lcpEntries = performance.getEntriesByType('largest-contentful-paint');
const fcpEntries = performance.getEntriesByType('paint').filter(e => e.name === 'first-contentful-paint');

JSON.stringify({
  fcp: fcpEntries.length > 0 ? fcpEntries[0].startTime : null,
  lcp: lcpEntries.length > 0 ? lcpEntries[lcpEntries.length - 1].startTime : null,
  domInteractive: perf ? perf.domInteractive : null,
  loadEvent: perf ? perf.loadEventEnd : null,
  transferSize: perf ? perf.transferSize : null
});
```

### PITFALL — Browser Timeout Fallback (CRITICAL)

`browser_navigate` can timeout (60s default) on JS-heavy or slow sites. **When this happens, switch to curl immediately — do not retry the browser.**

**Step 1: Performance via curl timing**

```bash
curl -s -o /tmp/audit-page.html -w "DNS:%{time_namelookup}|TCP:%{time_connect}|TLS:%{time_appconnect}|TTFB:%{time_starttransfer}|TOTAL:%{time_total}|SIZE:%{size_download}|HTTP:%{http_code}" "https://example.com/"
```

**Step 2: Extract HTML elements via grep**

```bash
# Title
grep -oP '<title>[^<]+</title>' /tmp/audit-page.html
# H1
grep -oP '<h1[^>]*>[^<]+</h1>' /tmp/audit-page.html
# Meta description
grep -oP 'name="description" content="[^"]+"' /tmp/audit-page.html
# Phone numbers
grep -oP '[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}' /tmp/audit-page.html | sort -u
# CTAs
grep -oiP '(book|reserve|contact|call|buy|sign up|submit)[^"<]{0,30}' /tmp/audit-page.html | sort -u
# Schema markup (count)
grep -c 'application/ld+json' /tmp/audit-page.html
# External CSS/JS
grep -oP '(href|src)="[^"]*\.(css|js)[^"]*"' /tmp/audit-page.html | wc -l
# Images
grep -c '<img ' /tmp/audit-page.html
```

**Step 3: Map curl timing to performance metrics**

| curl metric | maps to |
|---|---|
| `time_starttransfer` - `time_appconnect` | TTFB (server response time) |
| `time_total` | Estimated LCP |
| `time_starttransfer` | Estimated FCP |
| `time_total` + 500ms margin | Estimated TTI |
| `size_download` / 1024 | Page size KB |

### SEO Check

```javascript
// Via browser_console:
JSON.stringify({
  h1: document.querySelector('h1') ? document.querySelector('h1').textContent.trim() : null,
  title: document.title,
  metaDesc: document.querySelector('meta[name="description"]') ? document.querySelector('meta[name="description"]').content : null,
  hasSchema: !!document.querySelector('script[type="application/ld+json"]')
});
```

### Conversion Check

```javascript
const phoneRegex = /[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}/;
const bodyText = document.body.innerText;
const phoneMatch = bodyText.match(phoneRegex);
const ctaKeywords = ['book', 'call', 'contact', 'get started', 'schedule', 'reserve', 'order', 'buy', 'sign up', 'submit'];
const buttons = Array.from(document.querySelectorAll('a, button'));
const cta = buttons.find(b => ctaKeywords.some(k => b.textContent.toLowerCase().includes(k)));

JSON.stringify({
  hasPhone: !!phoneMatch,
  phone: phoneMatch ? phoneMatch[0] : null,
  hasCta: !!cta,
  ctaText: cta ? cta.textContent.trim() : null,
  hasForm: !!document.querySelector('form'),
  hasChat: !!document.querySelector('[class*="chat"], [id*="chat"], [class*="livechat"]')
});
```

## Gap Thresholds

| Metric | Good | Warning | Gap |
|--------|------|---------|-----|
| FCP | < 1.5s | 1.5-3s | > 3s |
| LCP | < 2.5s | 2.5-4s | > 4s |
| TTI | < 3s | 3-5s | > 5s |
| TTFB | < 0.8s | 0.8-1.5s | > 1.5s |
| Has H1 | Yes | - | No |
| Has CTA | Yes | - | No |
| Has Phone | Yes | - | No |
| Has Meta Desc | Yes | - | No |

## Gap Messaging

Each gap should include:
1. What's wrong (specific number)
2. Business impact (use specific numbers)
3. How JCE Media solves it

Example: "TTFB is 1.84s — server response is 2x slower than the 0.8s threshold. Google uses TTFB as a ranking signal, and visitors perceive slow response as unreliability. JCE Media's optimized landing pages respond in under 400ms."
