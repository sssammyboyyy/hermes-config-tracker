# NotebookLM Integration — Skill Scaffold

## Purpose
Integrate Google NotebookLM as a 24/7 free research backend for MAS audit generation. NotebookLM acts as a persistent knowledge base that ingests client website content, GBP reviews, competitor data, and brand materials — then serves as Hermes' query engine for truth-specific copy, competitor intelligence, and brand voice analysis during audit generation.

## Architecture

```
Hermes Agent → NotebookLM Skill → Browser Cookie Auth → NotebookLM API
                    ↓
            research/notebooklm/
                ├── client_sources/     # Uploaded URLs/PDFs per client
                ├── query_templates/    # Pre-built research queries
                └── output_cache/       # Cached query responses (TTL 24h)
```

## Authentication: Browser Cookie String

NotebookLM requires Google OAuth — no API key. Auth is via **browser cookie string** extracted from an authenticated Chrome session.

### Cookie Extraction Flow
1. User logs into https://notebooklm.google.com in Chrome
2. User opens DevTools → Application → Cookies → `https://notebooklm.google.com`
3. User copies the full cookie string (or specific tokens):
   - `HSID`, `SID`, `SSID`, `APISID`, `SAPISID`, `NID`
4. User provides cookie string to Hermes via one of:
   - **CLI param**: `--notebooklm-cookies "HSID=xxx; SID=xxx; ..."`
   - **Env var**: `NOTEBOOKLM_COOKIES="HSID=xxx; SID=xxx; ..."`
   - **Config file**: `~/.hermes/notebooklm-cookies.txt` (chmod 600)

### Cookie Storage Security
```bash
# Save cookies (one-time setup)
echo "HSID=xxx; SID=xxx; SSID=xxx; APISID=xxx; SAPISID=xxx" > ~/.hermes/notebooklm-cookies.txt
chmod 600 ~/.hermes/notebooklm-cookies.txt
```

Cookie string is sent as `Cookie:` header in all requests. Never logged, never committed to repos.

## System Prompt Template

When Hermes queries NotebookLM, it uses this system prompt to frame the research context:

```
You are the research intelligence layer for a Marketing Audit System (MAS) serving JCE Media, a South African AI-powered marketing agency. Your role is to provide accurate, specific competitive intelligence and brand analysis.

CONTEXT:
- ReviewTap sells NFC/QR review collection stands (warm leads already own this)
- JCE Media upsells AI marketing automation to ReviewTap clients
- Key metrics: 416% ROI, 65% lower CPL, 8.5x ROAS, $15M+ managed ad spend
- Target market: Hospitality (hotels/resorts), South Africa + international
- Typical client: 20-100 room hotel group, 500-5000 Google reviews

TASK:
Based ONLY on sources provided (client website, GBP data, competitor sites):

1. COMPETITOR ANALYSIS: For the target business and 3-5 local competitors, provide:
   - Rating comparison (reviews count + star average)
   - Key differentiators mentioned in positive reviews
   - Pain points mentioned in negative reviews
   - Service gaps (what competitors don't offer)

2. BRAND VOICE EXTRACTION: From the client's website and reviews:
   - Tagline/slogan
   - 3-5 key brand phrases used consistently
   - Tone (formal/casual, warm/corporate)
   - Unique selling propositions

3. PAIN POINT INTELLIGENCE: From negative GBP reviews:
   - Top 3 recurring complaints
   - Service inconsistency patterns
   - Specific quotes demonstrating frustration

4. COPY SUGGESTIONS: Based on all sources:
   - Headlines that reference real guest language
   - CTA copy that addresses known pain points
   - Value propositions grounded in actual differentiators

RULES:
- Cite specific sources for every claim
- If information is unavailable in sources, state "NOT IN SOURCES"
- Never fabricate reviews, ratings, or competitor details
- Prioritize specificity over generality
```

## Query Templates

Pre-built research queries stored in `references/query_templates/`:

### Template: Competitor Intelligence
```
Analyze the competitive landscape for [BUSINESS_NAME] in [LOCATION].
Target business: [NAME], [RATING] stars, [REVIEW_COUNT] reviews.
Competitors to compare: [COMP1], [COMP2], [COMP3].

For each competitor, extract:
1. Star rating and review count
2. Top 3 positive themes in reviews
3. Top 3 negative themes in reviews
4. Services mentioned (accommodation, conference, spa, etc.)

Output as a comparison table.
```

### Template: Pain Point Extraction
```
From the negative reviews of [BUSINESS_NAME], extract:
1. The top 5 most recurring complaints
2. Verbatim quotes that best represent each complaint
3. Any mention of competitor alternatives
4. Specific service failures (not just "bad service")
```

### Template: Brand Voice
```
Analyze the website content and positive reviews of [BUSINESS_NAME].
Extract:
1. The exact tagline/slogan
2. 5 key brand phrases used consistently
3. Tone analysis (formal/casual scale 1-10)
4. 3 unique selling propositions mentioned by guests
```

## Implementation Hook

The `notebooklm` skill is triggered during the **Research Phase** (Step 1 of the audit pipeline):

```
/step audit <url> <businessType>
  → [1] brand-asset-extractor     (scrape logo, images, colors, fonts)
  → [2] gbp-scraper               (Places API: ratings, reviews, photos)
  → [3] notebooklm-integration    (THIS SKILL — ingest sources, query intelligence)
  → [4] website-auditor           (curl-based perf + UX audit)
  → [5] mockup-generator          (generate HTML mockup with real data)
  → [6] report-assembly           (merge all into final HTML)
  → [7] deploy-validator          (pre-flight quality gate)
  → [8] git push gh-pages
```

## API Endpoint (Reverse-Engineered)

NotebookLM's web API (used via browser cookie auth):

```
POST https://notebooklm.google.com/_/NotebookLMUi/data/batchexecute
Content-Type: application/x-www-form-urlencoded
Cookie: <cookie_string>

Request params:
  - f.req: JSON-encoded request payload
  - at: Anti-CSRF token (from page load)

Response: JSON with query results, sources cited, and timestamps.
```

**Note**: The exact API endpoint and payload format requires further reverse-engineering. This scaffold provides the auth framework and prompt templates. Actual API integration is Phase 2.

## File Structure
```
~/.hermes/skills/deployed/notebooklm/
├── SKILL.md                          # This file
├── references/
│   ├── system_prompt.md              # Full system prompt template
│   ├── query_templates/
│   │   ├── competitor_intelligence.md
│   │   ├── pain_point_extraction.md
│   │   └── brand_voice.md
│   └── cookie_extraction_guide.md    # How to get cookies from Chrome
└── scripts/
    ├── notebooklm_query.py           # Query wrapper (Phase 2)
    └── source_ingestion.py           # Upload URLs/PDFs (Phase 2)
```

## Phase 1 vs Phase 2

**Phase 1 (Current — Scaffold)**:
- Cookie auth framework defined
- System prompt templates written
- Query templates created
- Pipeline integration point established
- Manual: user pastes NotebookLM responses into research data

**Phase 2 (Future — Automated)**:
- Reverse-engineer NotebookLM API
- Build `notebooklm_query.py` for automated queries
- Build `source_ingestion.py` for URL/PDF upload
- Cache query responses (TTL 24h)
- Full zero-touch integration into audit pipeline
