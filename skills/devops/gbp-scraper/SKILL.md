---
name: gbp-scraper
description: "Get Google Business Profile reviews, ratings, and response data via the Google Places API (New). No browser scraping — reliable and fast."
version: 2.0.0
author: MAS Orchestrator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [mas, gbp, google-business, places-api, reviews, ratings]
    related_skills: [marketing-audit]
---

# GBP Scraper — Google Business Profile Audit v2

Gets Google Business Profile data via the **Google Places API (New)**. No browser, no Puppeteer, no CAPTCHAs. Reliable and fast.

## Prerequisites

**Required:** `GOOGLE_PLACES_API_KEY` environment variable.

To get a key:
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Select your GCP project
3. Enable **Places API (New)** under APIs & Services → Library
4. Create an API key under APIs & Services → Credentials
5. Set as env var: `GOOGLE_PLACES_API_KEY=AIza...`

**PITFALL — Do NOT use Puppeteer for GBP scraping.** Google blocks headless browsers aggressively. CAPTCHAs, timeouts, and rate limits make it unreliable. The Places API is the only production-grade approach. Samuel explicitly flagged this: "Puppeteer is rather unreliable" for GBP work.

## Input

- `business_name` — the business to look up (e.g. "African Sky Hotels and Resorts")
- `temp_dir` — where to write `gbp-data.json` (default: `/home/samuelj121314/mas-system/temp/`)

## Output

`gbp-data.json` with structure:
```json
{
  "business_name": "African Sky Hotels and Resorts",
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
  "scraped_at": "2026-05-27T12:00:00Z",
  "source": "places-api"
}
```

## Method

### Step 1: Search for the Place

```bash
curl -s "https://places.googleapis.com/v1/places:searchText" \
  -H "Content-Type: application/json" \
  -H "X-Goog-Api-Key: $GOOGLE_PLACES_API_KEY" \
  -H "X-Goog-FieldMask: places.id,places.displayName,places.rating,places.userRatingCount,places.reviews,places.formattedAddress" \
  -d '{"textQuery": "<business_name> <city> <country>", "maxResultCount": 3}'
```

### Step 2: Get Place Details (if needed)

```bash
curl -s "https://places.googleapis.com/v1/places/<PLACE_ID>" \
  -H "X-Goog-Api-Key: $GOOGLE_PLACES_API_KEY" \
  -H "X-Goog-FieldMask: id,displayName,rating,userRatingCount,reviews,formattedAddress,websiteUri,regularOpeningHours,nationalPhoneNumber"
```

### Step 3: Parse and Write JSON

Parse the API response into the `gbp-data.json` structure. Compute:
- `response_rate` = reviews with responses / total reviews
- `avg_response_time_hours` = average hours between review and response (if response timestamps available)

### Fallback: Gap-Highlighting Dataset

If the API returns no results or the key is unavailable:
```json
{
  "found": false,
  "business_name": "<searched_name>",
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

- Places API free tier: generous quota
- If rate limited (429), wait 2 seconds and retry once
- If still failing, use fallback dataset

## Gap Analysis

After getting data, compute:
- `response_rate` = reviews with responses / total reviews
- If response_rate < 0.5 → flag as "Low response rate — AI auto-response recommended"
- If review_count < 50 → flag as "Low review volume — ReviewTap NFC stand can help"
- If avg_response_time > 24h → flag as "Slow response time — AI can respond instantly"
- If no GBP found at all → flag as critical gap (see fallback above)

## Cost

Places API (New) has a free tier. Text Search costs ~$0.031 per request. For audit pipeline usage (tens of runs/day), this stays within free tier or costs pennies. **Never use paid OpenRouter models for this — the API call is cheaper and more reliable.**
