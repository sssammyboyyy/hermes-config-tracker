---
name: quality-judge
description: "Evaluate the quality of MAS audit outputs — mockup, copy, brand fidelity, interactivity. Scores each dimension 1-10 and provides actionable feedback. Run before every deployment."
version: 1.0.0
author: MAS Orchestrator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [mas, quality, judge, evaluation, mockup, copy, brand]
    related_skills: [mockup-generator, marketing-audit]
---

# Quality Judge — MAS Output Evaluation

Evaluates every audit output before delivery. Nothing ships without passing.

## Evaluation Dimensions

### 1. Mockup Quality (1-10)
- **Real images**: Does the mockup use actual images from the client's site? (not emoji, not stock)
- **Brand fidelity**: Does it match the client's existing design language, colors, typography?
- **Layout quality**: Is it professional, modern, conversion-optimized?
- **Responsiveness**: Does it work on mobile?
- **Interactive elements**: Do all buttons, tabs, links work?

**Minimum score: 7/10 to ship**

### 2. Copy Quality (1-10)
- **Specificity**: Does it reference the client's actual business (name, location, reviews)?
- **Persuasion**: Does it create urgency and desire?
- **JCE Media positioning**: Are the stats (416% ROI, 65% lower CPL, 8.5x ROAS, $15M+) woven in naturally?
- **Gap narrative**: Is the collection vs. intelligence story compelling?
- **CTA clarity**: Is the next step obvious?

**Minimum score: 7/10 to ship**

### 3. Brand Fidelity (1-10)
- **Logo**: Is the client's actual logo used?
- **Colors**: Does it use the client's actual brand colors?
- **Typography**: Does it match the client's font choices?
- **Imagery**: Are real photos from the client's site used?
- **Voice**: Does the copy match the client's tone (luxury, professional, friendly)?

**Minimum score: 8/10 to ship** — Brand is sacred. Never guess.

### 4. Interactivity (1-10)
- **Navigation**: Do all tabs/buttons work?
- **Links**: Do all links resolve?
- **JavaScript**: Any console errors?
- **Cross-browser**: Works in Chrome, Firefox, Safari?
- **Mobile**: Touch targets work, no horizontal scroll?

**Minimum score: 9/10 to ship** — Broken interactivity kills credibility.

### 5. Technical Quality (1-10)
- **Self-contained**: No external dependencies that could break?
- **Protection layers**: All 6 layers present?
- **Performance**: Page loads fast?
- **Accessibility**: Alt text, semantic HTML?
- **SEO basics**: Title, meta description, H1?

**Minimum score: 7/10 to ship**

## Scoring Process

1. Open the mockup/report in a browser
2. Check every interactive element
3. Compare against the client's actual site
4. Score each dimension
5. If any dimension is below minimum, fix before shipping
6. Document scores in the audit output

## Output Format

```
QUALITY REPORT
==============
Mockup Quality:     8/10 ✅
Copy Quality:       7/10 ✅
Brand Fidelity:     9/10 ✅
Interactivity:      9/10 ✅
Technical Quality:  8/10 ✅
OVERALL:            8.2/10 ✅ SHIP

Issues found:
- None blocking
```

## Rules

1. **Never ship below minimums** — fix first, ship later
2. **Brand fidelity is non-negotiable** — if you can't get real assets, use a simpler design that doesn't fake them
3. **Interactivity must be perfect** — one broken button fails the entire report
4. **Copy must be specific** — generic copy is worse than no copy
5. **When in doubt, escalate to Samuel** — better to ask than to ship garbage
