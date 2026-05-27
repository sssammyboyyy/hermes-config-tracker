---
name: gbp-scraper
description: "Scrape Google Business Profile reviews, ratings, and response data using Puppeteer with stealth plugin. Falls back to gap-highlighting dataset on failure."
version: 1.0.0
author: MAS Orchestrator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [mas, gbp, google-business, scraper, puppeteer, stealth, reviews]
    related_skills: [marketing-audit]
---

# GBP Scraper — Google Business Profile Audit

Scrapes Google Business Profile data for the marketing audit pipeline.

## Input

- `business_name` or `url` — the business to look up
- `temp_dir` — where to write `gbp-data.json` (default: `/home/samuelj121314/mas-system/temp/`)

## Output

`gbp-data.json` with structure:
```json
{
  "business_name": "Example Hotel",
  "rating": 4.2,
  "review_count": 127,
  "response_rate": 0.35,
  "avg_response_time_hours": 48,
  "reviews": [
    {
      "author": "John D.",
      "rating": 5,
      "date": "2026-05-01",
      "text": "Great stay!",
      "response": null,
      "response_date": null
    }
  ],
  "scraped_at": "2026-05-26T12:00:00Z",
  "source": "google-business-profile"
}
```

## Method

### Option A: Puppeteer Stealth (Preferred)

Use the `mcp_puppeteer` tools with stealth:

```python
# Navigate to Google search for the business
mcp_puppeteer_puppeteer_navigate(url=f"https://www.google.com/search?q={business_name}+google+reviews")

# Wait for results, then extract
# Use mcp_puppeteer_puppeteer_evaluate to extract review data from the DOM
```

### Option B: Google Maps Scrape

```python
mcp_puppeteer_puppeteer_navigate(url=f"https://www.google.com/maps/search/{business_name}")
# Extract rating, review count, individual reviews
```

### Fallback: Gap-Highlighting Dataset

If scraping fails (CAPTCHA, rate limit, no results), return:
```json
{
  "business_name": "Unknown (scraping failed)",
  "rating": 0,
  "review_count": 0,
  "response_rate": 0,
  "avg_response_time_hours": null,
  "reviews": [],
  "scraped_at": "<ISO timestamp>",
  "source": "fallback",
  "gap": "No Google Business Profile data available — business is invisible to AI-powered review analysis. This alone represents a critical gap: without review data, no AI automation can be applied."
}
```

## Caching

Cache results for 24 hours in `/home/samuelj121314/mas-system/temp/gbp-cache/`. If a cached file exists and is < 24h old, return it instead of re-scraping.

## Rate Limiting

- Max 3 scrape attempts per run
- 5-second delay between attempts
- If CAPTCHA detected, immediately fall back to gap dataset

## Gap Analysis

After scraping, compute:
- `response_rate` = reviews with responses / total reviews
- If response_rate < 0.5 → flag as "Low response rate — AI auto-response recommended"
- If review_count < 50 → flag as "Low review volume — ReviewTap NFC stand can help"
- If avg_response_time > 24h → flag as "Slow response time — AI can respond instantly"
