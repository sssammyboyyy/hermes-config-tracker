---
name: marketing-audit
description: "Orchestrate the full MAS marketing audit pipeline — brand asset extraction, GBP scraping, website audit, mockup generation with real assets, report assembly, deployment, and quality evaluation."
version: 1.5.0
author: MAS Orchestrator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [mas, marketing-audit, orchestration, pipeline, reviewtap, jce-media]
    related_skills: [gbp-scraper, website-auditor, mockup-generator, quality-judge, usage-guardian]
---

# Marketing Audit — Pipeline Orchestrator v1.4

Coordinates all sub-agents to produce a single, protected HTML audit report with a separate AI-powered mockup page. Both use REAL brand assets extracted from the client's site.

## Trigger

`/goal audit <url> <businessType>`

## Execution Philosophy

**"Build first, prompt second."** Work around blocks, build what you can, ask only for what you truly cannot get.

**Every action must move the project forward.** If one approach fails, switch approach — don't stop.

## Pipeline Stages

```
Input: url + businessType
  │
  ├─ Stage 0: Brand Asset Extraction (curl → logo, hero images, colors, fonts)
  │            Upload to GitHub Pages /assets/ → verify 200 OK
  ├─ Stage 1: GBP Audit → gbp-data.json (Google Places API via curl)
  ├─ Stage 2: Website Audit → site-audit.json (curl, NO browser)
  ├─ Stage 3: Mockup Generation → mockup.html (SEPARATE file, real brand assets)
  ├─ Stage 4: Report Assembly → index.html (consolidated, tabbed, iframe → mockup.html)
  ├─ Stage 5: Deploy ALL to GitHub Pages (index.html + mockup.html + assets/)
  ├─ Stage 6: Quality Judge evaluation (quality-checklist.md — all must pass)
  │
  └─ Output: live URL + quality score + gap summary
```

## Stage Details

### Stage 0: Brand Asset Extraction (NEW in v1.4)

**Read `mockup-generator` skill → `references/brand-asset-extraction.md`**

1. Fetch homepage HTML via curl
2. Extract: logo URL, hero image URLs, brand colors (from CSS), font families
3. Download all assets to `/tmp/site_assets/`
4. Upload to GitHub Pages `/assets/` directory
5. Wait 5 seconds, verify HTTP 200 on all assets
6. Rewrite all URLs in mockup HTML to point to `https://USER.github.io/REPO/assets/`

### Stage 0.5: NotebookLM Enrichment (NEW in v1.6)

See `references/notebooklm-integration.md`. Upload client sources to NotebookLM for AI-powered research:
- Client website HTML
- GBP review data
- Competitor site data

Query for: competitor intelligence, pain point extraction, brand voice, copy suggestions. Cache for 24h.

### Stage 1: GBP Audit

Use `gbp-scraper` skill. Requires `GOOGLE_PLACES_API_KEY`. Returns real rating, reviews, phone, address.

### Stage 2: Website Audit

Use `website-auditor` skill. Use curl, NOT browser. Browser hangs on JS-heavy sites.

### Stage 3: Mockup Generation

Use `mockup-generator` skill (v2.1). Key requirements:
- **Separate `mockup.html` file** (never embed as base64 srcdoc in report)
- Real logo, real images, exact brand colors, exact brand fonts
- No emoji placeholders — ever
- Mobile responsive, all 6 protection layers

### Stage 4: Report Assembly

Build consolidated HTML with tabbed nav. JS function: `show(id,el)` for tab switching. Mockup section uses `<iframe src="<url>/mockup.html">`.

### Stage 5: Deployment

```bash
cp index.html mockup.html /tmp/gh-pages-deploy/
cp -r assets /tmp/gh-pages-deploy/
cd /tmp/gh-pages-deploy
git add -A && git commit -m "Deploy vX" && git push origin gh-pages --force
```

**After push — MANDATORY verification (non-negotiable):**
```bash
# Wait for GitHub Pages to propagate
sleep 10

# 1. Verify ALL assets return HTTP 200
for f in logo.png hero1.jpg hero2.jpg ...; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://USER.github.io/REPO/assets/$f")
  [ "$code" != "200" ] && echo "FAIL: $f returned $code" && exit 1
done

# 2. Verify report loads
curl -s -o /dev/null -w "Report: %{http_code}\n" "https://USER.github.io/REPO/"

# 3. Verify mockup loads
curl -s -o /dev/null -w "Mockup: %{http_code}\n" "https://USER.github.io/REPO/mockup.html"

# 4. Verify JS functions exist in report
curl -s "https://USER.github.io/REPO/" | grep -c 'function showTab'
curl -s "https://USER.github.io/REPO/" | grep -c 'function calcReportROI'
curl -s "https://USER.github.io/REPO/" | grep -c 'function speakSummary'

# 5. Verify JS functions exist in mockup
curl -s "https://USER.github.io/REPO/mockup.html" | grep -c 'function calcROI'
curl -s "https://USER.github.io/REPO/mockup.html" | grep -c 'function toggleChat'

# 6. Verify no HTML files served where images expected
curl -s "https://USER.github.io/REPO/assets/logo.png" | file - | grep -v "PNG\|JPEG" && echo "FAIL: asset is not an image"
```

**ALL checks must pass. If any fail, fix and redeploy. Never ship with broken assets.**

### Stage 5.5: File Verification (NEW)

Before deploying, verify all downloaded assets are actual images (not HTML pages):
```bash
for f in /tmp/assets/*; do
  type=$(file "$f" | grep -o "PNG\|JPEG\|GIF\|WebP")
  [ -z "$type" ] && echo "FAIL: $(basename $f) is not an image (got: $(file $f))" && exit 1
done
```

### Stage 6: Quality Judge

Run `quality-judge` checklist. All items must pass before considering the audit complete.

## Model Selection

**Use `model_registry.py` for ALL OpenRouter calls. Never hardcode model names.**

The daemon maintains `/home/samuelj121314/daemon/model_registry.py` with an intelligent task-based selector. Import it:

```python
import sys; sys.path.insert(0, '/home/samuelj121314/daemon')
from model_registry import get_model_for_task
result = get_model_for_task("mockup_generation")  # or any task key
```

**Task-to-model routing (all free-tier):**

| Task | Model | Why |
|------|-------|-----|
| Mockup / screenshot-to-code | `gemini-2.0-flash-001:free` | Vision capable |
| HTML generation (fast) | `gemini-2.0-flash-lite-preview-02-05:free` | Speed |
| Audit reasoning / strategy | `deepseek-r1:free` | Chain-of-thought |
| Report narrative / copy | `llama-4-maverick:free` | Quality writing |
| Code / technical | `deepseek-chat:free` | Accuracy |
| Fallback | `openrouter:auto:free` | Auto-route |

**Before ANY OpenRouter call**: check `usage-guardian` first. All models must be `:free` suffix. Paid models are blocked.

## Critical Pitfalls

### PITFALL — Mockup must be a separate file
Mockup = separate `mockup.html`, loaded via `iframe src="<url>/mockup.html"`.
**NEVER embed as base64 srcdoc** — regex patch operations on the report corrupt large embedded content.

### PITFALL — JS function name consistency
Function name in definition must match name in ALL onclick handlers. No console error when this breaks — tabs just silently fail.

### PITFALL — Puppeteer for GBP
**NEVER.** Google blocks headless browsers. Use Places API.

### PITFALL — No emoji placeholders
If you can't extract real images, use a clean text-only design. Emoji = amateur.

### PITFALL — GitHub Pages propagation delay
After push, wait 3-5 seconds before verifying URLs. Assets may return 404 initially.

### PITFALL — write_file truncation
For files >20KB, verify output size. Use Python for large files.

## Deployment

**GitHub Pages** (NOT Netlify — Netlify CLI OOMs on e2-micro during npm install).

## Key Metrics (hardcode in every report)

- 416% ROI
- 65% lower CPL
- 8.5x ROAS
- $15M+ managed ad spend

## Version Notes

**Deployment**: For persistent background daemon deployment via tmux, see `references/tmux-daemon-deployment.md`.

v1.5 (2026-05-28): Added intelligent model routing via model_registry.py. Added tmux daemon deployment reference. All model selection is now task-based.
v1.4: Added Stage 0 (brand asset extraction). Mockup uses real client assets. Added Stage 6 (quality judge). Reference to quality-checklist.md.
v1.3: Consolidated HTML report pattern, JS pitfall docs, GitHub Pages deployment.
v1.2: Places API integration, model routing table, build-first-prompt-second.
v1.1: Initial consolidated report with tabbed navigation.
v1.0: Basic pipeline.