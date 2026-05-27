---
name: mas-pipeline-patterns
description: "Compound intelligence: every lesson learned, mistake avoided, and win reinforced from MAS audit pipeline runs. Load before every audit."
version: 1.0.0
author: MAS Orchestrator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [mas, patterns, lessons, mistakes, wins, compounding, memory]
    related_skills: [marketing-audit, mockup-generator, gbp-scraper, quality-judge]
---

# MAS Pipeline Patterns — Compounding Intelligence

Every audit run MUST load these patterns. They prevent repeated mistakes and reinforce what works.

## CRITICAL MISTAKES (Never Repeat)

### 1. Regex Corrupts Large Base64 srcdoc
**Problem**: Attempting to regex-replace a large base64 data URI embedded in HTML srcdoc corrupted the entire file, breaking CSS/JS.
**Fix**: ALWAYS use separate HTML files for iframe `src` attributes. Never embed large base64 in srcdoc.
**Pattern**: `iframe src="https://site.com/mockup.html"` NOT `iframe srcdoc="data:text/html;base64,..."`

### 2. API Keys with Special Chars Break Python Strings
**Problem**: Reading API keys containing `/`, `+`, `=`, `*` from .env files into Python string literals caused SyntaxError.
**Fix**: ALWAYS read API keys via `os.environ.get("KEY")` or shell `grep | cut`. Never inline in Python code.

### 3. JS Function Name Mismatch
**Problem**: Nav HTML called `showSection()` but JS defined `function show()` — buttons appeared but didn't work.
**Fix**: ALWAYS verify both sides — grep for `onclick="` and `function NAME(` after every HTML write.

### 4. npm install OOM on e2-micro
**Problem**: `npm install -g netlify-cli` killed the process (exit -9/SIGKILL) on 1GB RAM e2-micro.
**Fix**: GitHub Pages for deployment. Never npm install anything >50MB on e2-micro.

### 5. Mockup Quality Without Real Assets
**Problem**: Used emoji placeholders (🏨, 🌍) and generic copy ("South Africa's Finest Hotels"). Rated 6/10.
**Fix**: ALWAYS scrape and use REAL assets: logo, hero images, brand colors, real copy from the client's site.
**v2 Upgrade**: Use custom SVG icons (72+ per mockup) — never emoji. Every icon is a hand-crafted SVG matching brand style. AI section must match hero quality — same design language, same attention to detail. Include AI comparison table, stat cards with real metrics, and JCE proof points.

### 6. Generic Copy Instead of Truth-Based Copy
**Problem**: "Experience South Africa's Finest Hotels" — generic, could be any hotel.
**Fix**: Use client's ACTUAL tagline ("WHERE WOULD YOU LIKE TO STAY?"), ACTUAL property names, ACTUAL locations, ACTUAL review quotes.

### 7. Not All GBP Properties Discovered
**Problem**: Only found the main GBP (5 reviews). Missed 4 other property GBPs (3,024 total reviews).
**Fix**: ALWAYS search Places API for each property name individually. Sum total reviews across all properties.

### 8. Not Researching Competitors
**Problem**: Generic "competitors are winning" narrative with no data.
**Fix**: ALWAYS query Places API for "hotels in [city]" for each property area. Use real competitor names, ratings, review counts.

## CRITICAL WINS (Reinforce)

### 1. Separate Mockup File Pattern
Mockup as standalone HTML page, loaded via `iframe src="URL"` — allows the mockup to be shared independently AND embedded in the report. Double value.

### 2. Google Places API for GBP
Works reliably, returns real ratings + review counts + review text + phone + address. No Puppeteer needed.

### 3. Brand Asset Scraping Pipeline
curl HTML → grep for images/colors/fonts → download assets → host on GitHub Pages → reference in mockup. Produces professional, brand-accurate results.

### 4. GitHub Pages Deploy Pattern
Copy files to `/tmp/gh-pages-deploy/` → git init → add → commit → push `--force` to `gh-pages` branch. Works every time.

### 5. Quality Judge Checklist
22-point checklist covering: real assets, brand colors, fonts, interactivity, protection layers. Catches issues before Samuel does.

### 6. Research Data JSON
Save all research to `/tmp/research_data.json` — single source of truth for mockup builder. Includes: properties, competitors, brand, reviews.

## PIPELINE ORDER (Do Every Time)

1. **Research Phase** (never skip)
   - curl client HTML → extract text, images, colors, fonts, phone, email
   - Places API → search each property name → get ratings, reviews, addresses
   - Places API → search competitors in each area
   - Save everything to `/tmp/research_data.json`

2. **Asset Phase**
   - Download logo → `/tmp/assets/logo.png`
   - Download hero images → `/tmp/assets/DALF*.jpg`
   - Upload assets to GitHub Pages `/assets/` folder
   - Verify assets accessible (HTTP 200)

3. **Mockup Phase**
   - Build using REAL data from research_data.json
   - Real logo, real images, real colors, real fonts
   - Real copy based on actual reviews and site content
   - Real phone numbers and emails per location
   - Separate HTML file (not embedded)
   - Run quality judge → fix failures → re-run until 9+/10

4. **Report Phase**
   - Clean HTML with working JS (verify function name matching)
   - iframe src="mockup.html" (separate file)
   - ROI calculator, voice button, copy link
   - All 6 protection layers
   - Run quality judge → fix → re-run

5. **Deploy Phase**
   - Copy to `/tmp/gh-pages-deploy/`
   - git add → commit → push `--force`
   - Wait 3-5 seconds
   - Verify HTTP 200 on all files
   - Run final quality judge on LIVE URLs

## QUALITY THRESHOLDS

- Mockup: 9/10 minimum (brand fidelity 10/10)
- Copy: 9/10 minimum (specific, truth-based, persuasive)
- Interactivity: 10/10 (every button works)
- Technical: 8/10 minimum
- Overall: 9/10 minimum to ship

## ESCALATION RULE

If quality judge scores below threshold after 2 fix iterations, escalate to Samuel with specific issues. Never ship below 8/10.
