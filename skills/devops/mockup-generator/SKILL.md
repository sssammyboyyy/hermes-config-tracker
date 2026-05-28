---
name: mockup-generator
description: "Generate a protected HTML mockup using real client brand assets (logo, images, colors, fonts). Separate file deployment."
version: 2.3.0
author: MAS Orchestrator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [mas, mockup, screenshot, vision, openrouter, protected-html, image-extraction]
    related_skills: [marketing-audit, karpathy-guidelines, openrouter-agents]
---

# Mockup Generator — Protected HTML Mockup v2.2

Generates a protected HTML mockup using the client's REAL brand assets (logo, hero images, colors, fonts).

**CRITICAL: Extract real brand assets FIRST, then build the mockup. Never use emoji placeholders.**

## Model Selection for Vision & Generation Tasks

**Use `model_registry.py` for ALL OpenRouter calls. Never hardcode model names in prompts.**

The daemon maintains `/home/samuelj121314/daemon/model_registry.py` with:
- `FREE_MODEL_REGISTRY`: Full catalog of free-tier models with specialties, speed tiers, and best-use metadata
- `TASK_ROUTING`: Task-to-model mapping (e.g., `mockup_generation` → `gemini-2.0-flash-001:free` for vision, `html_mockup` → `gemini-2.0-flash-lite-preview-02-05:fast` for fast code)
- `get_model_for_task(task)`: Returns optimal model dict for a given task

**Usage in any agent making LLM calls:**
```python
import sys
sys.path.insert(0, '/home/samuelj121314/daemon')
from model_registry import get_model_for_task

result = get_model_for_task("mockup_generation")
# result = {"model_id": "google/gemini-2.0-flash-001:free", "speed_tier": "medium", ...}
```

The canonical model registry lives at `/home/samuelj121314/daemon/model_registry.py` and is also mirrored in this skill at `scripts/model_registry.py`.

**When to use which model class:**
| Task Type | Registry Key | Why |
|-----------|-------------|-----|
| Screenshot-to-code / vision | `mockup_generation` | Gemini Flash vision capable |
| Fast HTML generation | `html_mockup` | Flash Lite is fast + cheap |
| Deep audit reasoning | `gap_synthesis` | DeepSeek R1 chain-of-thought |
| Professional copy / narrative | `report_narrative` | Llama 4 Maverick quality |
| Code / technical output | `roi_calculation` | DeepSeek Chat accuracy |

Before making any OpenRouter call, check `usage-guardian` first. All models are free-tier (`:free` suffix) — if a paid model is requested, the call must be blocked.

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

**Read `references/html-generation-technique.md` for the correct Python pattern.**

Create a **separate `mockup.html` file** (NOT embedded in the report). Requirements:
- **Real logo** in header (not text placeholder)
- **Real hero images** with slider/carousel
- **Exact brand colors** from extraction
- **Exact brand fonts** (Google Fonts `<link>`)
- **Real phone number** in header (clickable `tel:` link)
- **Real Google reviews** in social proof section (include at least one negative review for honesty — red left border)
- **Property cards with real images** — each card links to property-specific email (`property@client.com`) and phone
- **Badges**: "TOP RATED" for highest-rated properties, "NEEDS ATTENTION" for below-average
- **Competitor comparison section** — show each property vs. local competitor with real rating data, color-coded better/worse/same badges
- **AI features section** (if pitching JCE Media) with comparison table (Collection vs. Intelligence)
- **Chat widget** — floating button + modal using CSS `.show` class toggle (NOT inline style)
- **ROI calculator** (JS-driven, works offline)
- **JCE stats section** (416% ROI, 65% lower CPL, 8.5x ROAS, $15M+)
- **Mobile responsive**
- **All 6 protection layers**

#### CRITICAL: File Writing Pattern

Write template to `/tmp/template.html` with `{{PLACEHOLDER}}` markers. Build dynamic sections via Python string concatenation. Substitute with `.replace()`. Never use f-strings for HTML+JS.

### Step 4: Deploy Mockup as Separate File

Copy mockup.html to gh-pages deploy dir and push. **NEVER embed as base64 srcdoc** — regex patch operations on the report file corrupt large embedded content.

### Step 5: Reference in Report

```html
<iframe src="https://USER.github.io/REPO/mockup.html"></iframe>
<a href="https://USER.github.io/REPO/mockup.html" target="_blank">Open mockup in new tab →</a>
```

## Quality Standards (run quality-judge before shipping)

- Mockup uses real images (not emoji): **≥ 9/10**
- Brand fidelity (colors, fonts, logo match client site): **≥ 9/10**
- All interactive elements work: **≥ 9/10**
- Copy specific to client (name, location, reviews): **≥ 9/10**
- Competitor data present and real: **≥ 9/10**

## Protection Layers (ALL 6 required)
## Quality Standards (MUST pass before shipping — no exceptions)

- Mockup uses real images verified via `file` command (not emoji, not HTML masquerading as images): **≥ 9/10**
- Brand fidelity (colors, fonts, logo match client site): **≥ 9/10**
- All interactive elements work (chat, ROI calc, tabs, links): **≥ 9/10**
- Copy specific to client (name, location, reviews), NOT generic: **≥ 9/10**
- Competitor data present and real: **≥ 9/10**
- **Problem→Solution narrative**: Mockup demonstrates exact client pain points AND shows JCE Media's solution within the mockup itself: **≥ 9/10**

## ⚠️ CRITICAL: Why v2 Failed — Learn This or Repeat

**"v2 is worse than v1"** — Samuel's exact words. The mockup was technically functional but failed as a sales weapon because:

1. **No pain point demonstration**: The mockup showed a pretty site but didn't VISUALLY show what's broken (e.g., "0% review response rate" as a visible gap, unresponsive reviews, slow load time)
2. **No solution demonstration**: AI features were listed but not shown in action (chat widget that actually responds, auto-routed feedback, instant lead capture)
3. **Not client-specific enough**: Could have been any hotel group. Missing: actual property names in context, actual review quotes as headlines, actual competitor names
4. **Missing the "before/after" narrative**: The client needs to see their current pain AND the proposed solution in ONE view

**RULE: Every mockup must answer "Why should this client pay for JCE Media?" within 5 seconds of viewing.**

If the mockup doesn't show a visible gap (pain) AND the AI-powered fix (solution), it's just a web design exercise — not a sales weapon.

### Problem→Solution Narrative (CRITICAL — what makes this a sales weapon)
The mockup must NOT just be a prettier version of the client's site. It must:
1. **Show the pain point**: E.g., "0% review response rate" displayed as a visible gap
2. **Demonstrate the solution**: E.g., AI chat widget that responds in 60 seconds, auto-routed negative feedback
3. **Prove the transformation**: E.g., "From 3,000 reviews to 10,000" / "From manual to AI-powered"
4. **Include real data**: Actual property names, actual review quotes, actual competitor comparisons
5. **Be client-specific**: Should be impossible to mistake this mockup for a generic template

This is what makes the deliverable survive customer criticism and serve as the main sales weapon.

## Error Recovery

1. **SyntaxError in generated HTML JS** → Check for f-string usage. Switch to string concatenation + template substitution pattern.
2. **Image extraction fails / images are HTML pages** → Run `file` command on every downloaded asset. If MIME type is not image (PNG/JPEG), the URL is wrong. Scrape the live site HTML to find correct URLs (common: `/uploads/YYYY/MM/` where YYYY/MM varies). Try multiple path patterns. If still failing, use GBP data + clean text-only mockup.
3. **GitHub Pages 404 on deploy** → Wait 5 seconds and retry (propagation delay). Verify URL pattern matches gh-pages branch structure.
4. **Fonts not loading** → Use system font stack fallback
5. **Colors not extracting** → Safe defaults: navy #2e3365, teal #31cdcf
6. **Chat modal not opening** → Verify CSS has `.cm.show { display: flex; }` rule and JS uses `classList.toggle('show')` not inline style
7. **Regex corrupts HTML** → Regex replacements on large HTML files break JS/CSS. Use template + placeholder substitution instead

## Version Notes

v2.3: Added image verification requirement (`file` command). Added problem→solution narrative as critical quality dimension. Strengthened error recovery for image URL failures. Quality threshold raised to 9/10 across ALL dimensions including narrative.
v2.2: Added f-string/JS curly brace technique warning (references/html-generation-technique.md). Added per-property booking links pattern. Added competitor comparison section. Added negative review card pattern. Added chat widget `.show` CSS pattern. Added post-deploy verification checklist. Quality threshold raised to 9/10 across all dimensions.
v2.1: Added brand asset extraction guide (references/brand-asset-extraction.md).
v2.0: Real image/logo extraction from target site.