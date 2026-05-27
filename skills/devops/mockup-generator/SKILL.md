---
name: mockup-generator
description: "Generate a protected HTML mockup using real client brand assets (logo, images, colors, fonts). Separate file deployment."
version: 2.1.0
author: MAS Orchestrator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [mas, mockup, screenshot, vision, openrouter, protected-html, image-extraction]
    related_skills: [marketing-audit, karpathy-guidelines, openrouter-agents]
---

# Mockup Generator — Protected HTML Mockup v2.1

Generates a protected HTML mockup using the client's REAL brand assets (logo, hero images, colors, fonts).

**CRITICAL: Extract real brand assets FIRST, then build the mockup. Never use emoji placeholders.**

## Method

### Step 1: Extract Real Brand Assets

**Read `references/brand-asset-extraction.md` for the full extraction guide.**

Use curl + regex to extract from the client's homepage HTML:
- Logo URL (search for `logo` in img src/class)
- Hero/property images (all img tags, data-src, srcset)
- Brand colors (fetch CSS, count hex color frequency)
- Font families (Google Fonts links, font-family declarations)
- Phone, address (from GBP data)

Download all assets to `/tmp/site_assets/`.

### Step 2: Upload Assets to GitHub Pages

```bash
cp -r /tmp/site_assets /tmp/gh-pages-deploy/assets
```

Rewrite all image URLs in the mockup HTML to point to `https://USER.github.io/REPO/assets/FILENAME`.

### Step 3: Build Mockup HTML

Create a **separate `mockup.html` file** (NOT embedded in the report). Requirements:
- **Real logo** in header (not text placeholder)
- **Real hero images** with slider/carousel
- **Exact brand colors** from extraction
- **Exact brand fonts** (Google Fonts `<link>`)
- **Real phone number** in header (clickable `tel:` link)
- **Real Google reviews** in social proof section
- **Property cards with real images**
- **AI features section** (if pitching JCE Media)
- **Chat widget** (floating button)
- **Mobile responsive**
- **All 6 protection layers**

### Step 4: Deploy Mockup as Separate File

Copy mockup.html to gh-pages deploy dir and push. **NEVER embed as base64 srcdoc** — regex patch operations on the report file corrupt large embedded content because braces in the base64 string interfere with pattern matching.

### Step 5: Reference in Report

```html
<iframe src="https://USER.github.io/REPO/mockup.html"></iframe>
<a href="https://USER.github.io/REPO/mockup.html" target="_blank">Open mockup in new tab</a>
```

## Quality Standards (run quality-judge before shipping)

- Mockup uses real images (not emoji): **≥ 7/10**
- Brand fidelity (colors, fonts, logo match client site): **≥ 8/10**
- All interactive elements work: **≥ 9/10**
- Copy specific to client (name, location, reviews): **≥ 7/10**

## Protection Layers (ALL 6 required)

1. CSS watermark — "ReviewTap x JCE Media" tiled diagonally
2. Right-click disabled — `<body oncontextmenu="return false;">`
3. Keyboard shortcuts blocked — Ctrl+S, Ctrl+U, Ctrl+P, F12
4. DevTools detection — debugger loop
5. Canvas pixel scrambling — requestAnimationFrame noise
6. Transparent overlay — full-viewport div

## Error Recovery

1. Image extraction fails → Use GBP data + clean text-only mockup (no fake images)
2. GitHub Pages 404 on deploy → Wait 5 seconds and retry (propagation delay)
3. Fonts not loading → Use system font stack fallback
4. Colors not extracting → Safe defaults: navy #2e3365, teal #31cdcf

## Version Notes

v2.1: Added brand asset extraction guide (references/brand-asset-extraction.md). Mockup must be separate file with real images uploaded to GitHub Pages. Added quality standards. Never use emoji placeholders.
v2.0: Real image/logo extraction from target site.