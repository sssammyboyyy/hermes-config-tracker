# MAS — Marketing Audit & Strategy

Multi-agent marketing audit pipeline built on Hermes.
Generates protected, self-contained HTML audit reports that quantify the gap
between basic review collection (ReviewTap) and AI-powered automation (JCE Media).

## Structure

```
SOUL.md                     # MAS Orchestrator spec (Hermes system prompt)
skills/devops/              # 5 core pipeline skills
  marketing-audit/          # Orchestrator — receives /goal audit <url> <businessType>
  gbp-scraper/              # Google Business Profile scraping via Puppeteer stealth
  website-auditor/          # Web performance + SEO + conversion audit
  mockup-generator/         # Screenshot → OpenRouter Vision → protected HTML mockup
  usage-guardian/           # API call tracker (200/day, 10/min limits)
mas-system/
  report-template.html      # Self-contained HTML report template with protection layers
```

## Key Metrics (ReviewTap → JCE Media)

- **416% ROI**
- **65% lower CPL**
- **8.5× ROAS**
- **$15M+ managed ad spend**

## Usage

```
/goal audit <url> <businessType>
```

Example: `/goal audit https://www.example.com Hotel Owner`

## Requirements

- Hermes Agent (hermes-agent.nousresearch.com)
- OpenRouter API key (free tier)
- Puppeteer + Chromium (auto-installed)

## Pipeline

1. **GBP Audit** → Google Business Profile reviews/ratings/response data
2. **Website Audit** → FCP, LCP, TTI, SEO, conversion gaps
3. **Mockup Generation** → Protected HTML mockup using real brand assets
4. **Report Assembly** → All data merged into self-contained HTML report

## License

Private — ReviewTap × JCE Media
