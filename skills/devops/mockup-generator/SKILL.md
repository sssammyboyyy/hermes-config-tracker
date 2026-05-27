---
name: mockup-generator
description: "Take a full-page screenshot of a website, extract real images/logos, send to OpenRouter Vision with intelligent model selection, and generate a protected HTML mockup."
version: 2.0.0
author: MAS Orchestrator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [mas, mockup, screenshot, vision, openrouter, protected-html, image-extraction]
    related_skills: [marketing-audit, karpathy-guidelines, openrouter-agents]
---

# Mockup Generator — Protected HTML Mockup v2

Generates a protected HTML mockup reusing the client's REAL brand assets (logos, images, colors).

**CRITICAL: Load `karpathy-guidelines` skill before generating any HTML. Maximum 250 lines of self-contained HTML, no external frameworks.**

**CRITICAL: Load `openrouter-agents` skill for model selection. Use the routing decision tree — mockup generation = `google/gemini-2.0-flash-001:free` (vision) → escalate to `openrouter/owl-alpha` if insufficient.**

## Input

- `url` — the website to mock up
- `temp_dir` — working directory (default: `/home/samuelj121314/mas-system/temp/`)
- `output_dir` — where to write `protected-mockup.html` (default: same as temp_dir)

## Output

`protected-mockup.html` — self-contained HTML with real brand assets + all 6 protection layers.

## Method

### Step 1: Navigate + Extract Real Brand Assets

Navigate with Puppeteer, then run JS to extract all images/logos/brand assets. See `references/image-extraction.md` for the full JS helper and download pattern.

```
NAVIGATE to url via mcp_puppeteer_puppeteer_navigate

EVALUATE JS to extract images:
  - All img[src] with width > 50px
  - Background images from header, hero, logo, banner elements
  - SVG logo hrefs
  - Sort by size (largest first)

DOWNLOAD extracted images to temp_dir:
  - Logo → extracted_logo.png
  - Hero image → extracted_hero.png
  - Top 4 content images → extracted_1.jpg ... extracted_4.jpg
  - Make relative URLs absolute using site origin

SCREENSHOT full page → audit-mockup.png
```

### Step 2: Smart Model Selection for Vision

Use the openrouter-agents routing decision tree:

```
Vision task with images?
  → Primary: google/gemini-2.0-flash-001:free
  → Fallback: openrouter/owl-alpha (if context > 100K or gemini fails)
  → NEVER use paid models
```

### Step 3: Generate Mockup with Real Assets

Send to vision model with this prompt:

```
CONVERSION RATE OPTIMIZATION EXPERT — Generate improved mockup HTML.

MANDATORY:
- Reuse the business's REAL logo (extracted and attached)
- Extract and reuse their brand colors from the screenshot
- Use their actual product/hero images
- Maintain visual identity while improving conversion

LAYOUT REQUIREMENTS:
1. Hero section: value proposition + real imagery + CTA above fold
2. Phone number in header (visible)
3. Social proof section (reviews/testimonials)
4. Clean, modern design respecting existing brand
5. Mobile-responsive

OUTPUT: Only valid HTML, self-contained, inline CSS. Reference local image paths.
```

### Step 4: Inject Protection Layers

ALL 6 layers required (see below). Write to `protected-mockup.html`.

### Step 5: Copy Extracted Images

Copy all downloaded brand images alongside the HTML so they resolve locally.

## Protection Layers

### Layer 1: CSS Watermark
```html
<style>
.watermark { position:fixed; top:0; left:0; right:0; bottom:0; pointer-events:none; z-index:99999; background:repeating-linear-gradient(-45deg, transparent, transparent 40px, rgba(0,0,0,0.03) 40px, rgba(0,0,0,0.03) 80px); }
.watermark::after { content:"ReviewTap x JCE Media"; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%) rotate(-30deg); font-size:48px; color:rgba(0,0,0,0.06); white-space:nowrap; pointer-events:none; }
</style>
<div class="watermark"></div>
```

### Layer 2: Right-Click Disabled
```html
<body oncontextmenu="return false;">
```

### Layer 3: Keyboard Shortcuts Blocked
```html
<script>
document.addEventListener('keydown',function(e){if((e.ctrlKey||e.metaKey)&&['s','u','p','S','U','P'].includes(e.key)){e.preventDefault();return false;}if(e.key==='F12'){e.preventDefault();return false;}});
</script>
```

### Layer 4: DevTools Detection
```html>
<script>(function(){var d=/./;d.toString=function(){this.opened=true;};console.log('%c',d);setInterval(function(){if(d.opened){debugger;d.opened=false;}},500);})();</script>
```

### Layer 5: Canvas Pixel Scrambling
```html
<canvas id="scramble" style="position:fixed;top:0;left:0;width:1px;height:1px;opacity:0;z-index:-1;"></canvas>
<script>(function(){var c=document.getElementById('scramble');var ctx=c.getContext('2d');c.width=200;c.height=200;function noise(){var id=ctx.createImageData(200,200);for(var i=0;i<id.data.length;i++)id.data[i]=Math.random()*255;ctx.putImageData(id,0,0);requestAnimationFrame(noise);}noise();})();</script>
```

### Layer 6: Transparent Overlay
```html
<div style="position:fixed;top:0;left:0;width:100%;height:100%;z-index:99990;"></div>
```

## Cost Tracking

Log every OpenRouter call:
- Model used
- Timestamp
- Token count
- Purpose (mockup-generation)

## Error Recovery

1. Image extraction fails → Use screenshot only, prompt model to describe brand colors
2. Vision model fails → Escalate per openrouter-agents tiered escalation
3. Rate limit (429) → Switch to alternative free vision model
4. All vision fails → Use screenshot + heuristic HTML template with brand colors extracted via JS

## Version Notes

v2.0: Added real image/logo extraction from target site. Mockups now reuse actual brand assets.
