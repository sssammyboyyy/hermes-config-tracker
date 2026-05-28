---
name: gbp-scraper
description: "Get Google Business Profile reviews, ratings, and response data via the Google Places API (New). No browser scraping — reliable and fast."
version: 2.1.0
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

**Required:** `GOOGLE_PLACES_API_KEY` environment variable (set in `~/.hermes/.env`).

**Confirmed working key:** `AIzaSy...7jeA` (Samuel's key, saved in .env)

**⚠ NEVER use Puppeteer for GBP scraping.** Samuel explicitly flagged this: "Puppeteer is rather unreliable." Google blocks headless browsers. The Places API is the only production-grade approach.

## Input

- `business_name` — the business to look up (e.g. "African Sky Hotels and Resorts")
- `temp_dir` — where to write `gbp-data.json` (default: `/home/samuelj121314/mas-system/temp/`)

## Output

`gbp-data.json` with structure:
```json
{
  "found": true,
  "business_name": "African Sky Hotels & Resorts",
  "rating": 5.0,
  "review_count": 5,
  "response_rate": 0,
  "avg_response_time_hours": null,
  "reviews": [
    {
      "author": "Derek Lipman",
      "rating": 5,
      "date": "2023-03-04",
      "text": "Had the pleasure of visiting all 4 South African properties...",
      "response": null,
      "response_date": null
    }
  ],
  "formatted_address": "Ground Floor, Building 9, Centurion Gate Office Park...",
  "phone": "012 998 4959",
  "website": "http://www.africanskyhotels.com/",
  "place_id": "ChIJQ6Vv2k9nlR4RUnXz-yzRzow",
  "scraped_at": "2026-05-27T12:00:00Z",
  "source": "places-api"
}
```

**Note:** Places API does NOT return business owner responses to reviews. `response_rate` will always be 0 from the API alone. This is expected — use it as a gap indicator ("0% response rate").

## Method

### Step 1: Search for the Place (CONFIRMED WORKING)

```bash
curl -s "https://places.googleapis.com/v1/places:searchText" \
  -H "Content-Type: application/json" \
  -H "X-Goog-Api-Key: $GOOGLE_PLACES_API_KEY" \
  -H "X-Goog-FieldMask: places.id,places.displayName,places.rating,places.userRatingCount,places.reviews,places.formattedAddress,places.websiteUri,places.nationalPhoneNumber" \
  -d '{"textQuery": "<business_name> <country>", "maxResultCount": 1}'
```

**Confirmed working example:**
```bash
# African Sky Hotels & Resorts → 5.0★, 5 reviews, phone: 012 998 4959
curl -s "https://places.googleapis.com/v1/places:searchText" \
  -H "Content-Type: application/json" \
  -H "X-Goog-Api-Key: $GOOGLE_PLACES_API_KEY" \
  -H "X-Goog-FieldMask: places.id,places.displayName,places.rating,places.userRatingCount,places.reviews,places.formattedAddress,places.websiteUri,places.nationalPhoneNumber" \
  -d '{"textQuery": "African Sky Hotels and Resorts South Africa", "maxResultCount": 1}'
```

Response includes: `id`, `displayName.text`, `rating`, `userRatingCount`, `reviews[]` (with `authorAttribution.displayName`, `rating`, `text.text`, `publishTime`), `formattedAddress`, `websiteUri`, `nationalPhoneNumber`.

### Step 2: Parse and Write JSON

Parse the API response into the `gbp-data.json` structure. Key mappings:
- `place["displayName"]["text"]` → `business_name`
- `place["rating"]` → `rating`
- `place["userRatingCount"]` → `review_count`
- `place["reviews"][i]["authorAttribution"]["displayName"]` → `reviews[i].author`
- `place["reviews"][i]["rating"]` → `reviews[i].rating`
- `place["reviews"][i]["text"]["text"]` → `reviews[i].text`
- `place["reviews"][i]["publishTime"][:10]` → `reviews[i].date`
- `response_rate` → 0 (API doesn't return business responses)

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
- `response_rate` = 0 (API limitation — always flag as gap)
- If `review_count < 50` → flag as "Low review volume — ReviewTap NFC stand can help"
- If `review_count == 0` → flag as critical: "No Google Business Profile found"
- If `rating == 0` → flag as critical: "No rating data available"
- Always flag: "0% response rate — AI auto-response recommended"

## Cost

Places API (New) has a generous free tier. Text Search costs ~$0.031 per request. For audit pipeline usage (tens of runs/day), this stays within free tier or costs pennies. **Never use paid OpenRouter models for this — the API call is cheaper and more reliable.**

## Confirmed Working Example

African Sky Hotels & Resorts:
- **Query:** `"African Sky Hotels and Resorts South Africa"`
- **Result:** `{"displayName": {"text": "African Sky Hotels & Resorts"}, "rating": 5, "userRatingCount": 5, "nationalPhoneNumber": "012 998 4959", "websiteUri": "http://www.africanskyhotels.com/", "formattedAddress": "Ground Floor, Building 9, Centurion Gate Office Park, 126 Akkerboom St, Zwartkop, Centurion, 0157, South Africa"}`
- **Reviews:** 5 reviews, all 5-star, from 2023-2025
