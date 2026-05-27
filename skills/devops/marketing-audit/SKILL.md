---
name: marketing-audit
description: "Orchestrate the full MAS marketing audit pipeline — coordinates GBP scraping, website audit, mockup generation, and report assembly into a single protected HTML report."
version: 1.1.0
author: MAS Orchestrator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [mas, marketing-audit, orchestration, pipeline, reviewtap, jce-media]
    related_skills: [gbp-scraper, website-auditor, mockup-generator, usage-guardian]
---

# Marketing Audit — Pipeline Orchestrator

This is the top-level skill for the MAS (Marketing Audit & Strategy) pipeline. It coordinates all sub-agents to produce a single, protected HTML audit report.

## Trigger

Activated when the user sends: `/goal audit <url> <businessType>`

## Pipeline Stages

```
Input: url + businessType
  │
  ├─ Stage 1: GBP Audit Agent → gbp-data.json
  ├─ Stage 2: Website Audit Agent → site-audit.json
  ├─ Stage 3: Mockup Generation Agent → protected-mockup.html
  ├─ Stage 4: Report Assembly Agent → audit-<timestamp>.html
  │
  └─ Output: path to final HTML report + gap summary
```

## Execution Pattern

Stages run sequentially. Each stage writes its output to `/home/samuelj121314/mas-system/temp/`. A stage that fails does NOT abort the pipeline — use its fallback data and continue.

**PITFALL — Browser timeouts on heavy sites:** `browser_navigate` can timeout (60s default) on JS-heavy or slow sites. When this happens, do NOT retry the browser. Instead, use `curl` + `terminal()` to collect performance data. This fallback collected all needed data for africanskyhotels.com in under 5 seconds. See `website-auditor` skill for the full curl-based extraction method.

### After All Stages: Report Assembly

Use `execute_code` (Python) to:
1. Read all JSON outputs from `/home/samuelj121314/mas-system/temp/`
2. Read the template from `/home/samuelj121314/mas-system/report-template.html`
3. Replace `{{PLACEHOLDER}}` tokens with real data via Python `str.replace()`
4. Write the filled HTML to `/home/samuelj121314/mas-output/audit-<ISO8601>.html`

See `references/report-assembly.py` for a complete worked example.

### 0. Validate Input

```python
from urllib.parse import urlparse

def validate_url(url):
    parsed = urlparse(url if url.startswith('http') else f'https://{url}')
    if not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")
    return f"https://{parsed.netloc}"

VALID_TYPES = ["Hotel Owner", "Restaurant Owner", "Dentist", "Law Firm", "Real Estate", "Auto Dealer"]

def validate_business_type(bt):
    return bt if bt in VALID_TYPES else "Other"
```

### 1. GBP Audit Agent

Use `gbp-scraper` skill (v2 — Places API). Output: `gbp-data.json`.

**⚠ PITFALL — Do NOT use Puppeteer for GBP.** Samuel explicitly flagged this: "Puppeteer is rather unreliable." Google blocks headless browsers. Use the Google Places API via curl. Requires `GOOGLE_PLACES_API_KEY` env var. If the key is not set, the skill falls back to the gap-highlighting dataset — which is still a valid and compelling narrative.

**Fallback if API returns no results (no GBP):**

```json
{
  "found": false,
  "business_name": "Unknown (scraping failed)",
  "rating": 0,
  "review_count": 0,
  "response_rate": 0,
  "avg_response_time_hours": null,
  "reviews": [],
  "gap": "No Google Business Profile data available — business is invisible to AI-powered review analysis"
}
```

### 2. Website Audit Agent

Use `website-auditor` skill. Output: `site-audit.json`.

**Fallback if browser times out:** Use curl-based extraction (see `website-auditor` PITFALL section). Collect TTFB, total load time, page size, HTTP status, grep for H1/title/meta/phone/CTA/schema/resource counts from raw HTML. This is faster than the browser and does not hang.

### 3. Mockup Generation Agent

Use `mockup-generator` skill (v2). Output: `protected-mockup.html`.

**Key v2 improvement:** The mockup now extracts REAL brand assets (logo, hero images, product photos) from the target site via Puppeteer JS evaluation, downloads them locally, and includes them in the generated HTML mockup. This means prospects see their own brand imagery in the improved layout — much more persuasive than stock placeholders.

**Model selection (per openrouter-agents routing):**
- Vision/mockup generation → `google/gemini-2.0-flash-001:free`
- Escalate to `openrouter/owl-alpha` if output insufficient
- **NEVER use paid models**

**Fallback if mockup generation fails:** Include a placeholder div in the report explaining the timeout and suggesting re-run with `--mockup`.

### 4. Report Assembly Agent

Use `execute_code` with Python. Merge all JSON data + mockup into the `{{PLACEHOLDER}}` template. Write to `/home/samuelj121314/mas-output/audit-<ISO8601>.html`.

## Error Recovery

For each stage:
1. Attempt the stage
2. If it fails, retry once automatically **with a changed approach** (e.g., browser → curl, not browser → browser)
3. If retry fails, use fallback data and continue
4. Never abort the entire pipeline for one failed stage
5. On first encounter of a new failure class, create an error-recovery skill for it

## Key Metrics (hardcode in every report)

- 416% ROI
- 65% lower CPL
- 8.5x ROAS
- $15M+ managed ad spend

## Gap Narrative

The report must highlight the gap between:
- **Collection** (ReviewTap NFC/QR stands) — what the business currently has
- **Intelligence** (JCE Media AI automation) — what they're missing

Gap indicators:
- Low review response rate (< 50%) → needs AI auto-response
- No review routing → needs smart positive/negative routing
- Slow website LCP (> 2.5s) → losing leads before they convert
- Missing CTA/phone on website → no conversion path
- Zero automation → all reviews handled manually or ignored

## Output Format

Final response must contain:
1. Full path to generated HTML report
2. Time taken (target < 90 seconds)
3. Summary of gaps found (as Telegram message to user)
4. Key metrics comparison (current vs. with JCE Media)

## Temp File Cleanup

After report generation, clean up `/home/samuelj121314/mas-system/temp/` but keep the final HTML report.

## Skill Library Hygiene

Keep the skill library lean. After cleanup work or major sessions:
- Delete unused skill categories from `~/.hermes/skills/` (keep only `devops/` for MAS work)
- Delete Puppeteer cache (`~/.cache/puppeteer/`) if not needed immediately
- Delete `node_modules/puppeteer` if Chromium cache was cleared
- Force-push lean GitHub repos to remove history bloat

See `hermes-config` skill references for detailed cleanup procedures.

## Exponential Refinement Tracking

Every audit run should contribute to compounding improvement. After each audit:

1. **Log changes**: The `hermes-improvement-logger` cron job (daily) checks for recently modified `SKILL.md` files and appends summaries to `~/workspace/improvement-log.md`
2. **Track skill versions**: When a skill is updated during an audit (error recovery, new technique), bump its version in the YAML frontmatter
3. **Capture new patterns**: If a new fallback, workaround, or technique was discovered, update the relevant skill immediately — don't wait
4. **Report improvements**: In the audit summary, include a line about any system improvements made during the run

The improvement log at `~/workspace/improvement-log.md` serves as a growth diary — reviewing it shows the trajectory of system capability over time.
