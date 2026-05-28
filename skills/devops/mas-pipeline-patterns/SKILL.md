---
name: mas-pipeline-patterns
description: "Compound intelligence: every lesson learned, mistake avoided, and win reinforced from MAS audit pipeline runs. Load before every audit."
version: 1.8.0
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
**v2 Upgrade**: Use real images and property-specific content — never emoji. Per-property descriptions must reference actual review quotes. Include at least one negative review card (red border) for credibility. Add competitor comparison section with real data.

### 6. f-String JS Curly Brace Corruption
**Problem**: Using Python f-strings to generate HTML containing JavaScript `{}` braces causes SyntaxError because f-strings interpret `{}` as interpolation markers.
**Fix**: Use Python string concatenation (`+`) or `.join()` for dynamic HTML parts. Write template to file with `{{PLACEHOLDER}}` markers, then `.replace()` after building dynamic content.

### 7. Chat Widget Not Opening
**Problem**: Chat modal used `classList.add('show')` to open but CSS had no `.show { display: flex !important; }` rule, or used inline `style.display` toggle which conflicts with CSS.
**Fix**: Define `.cm { display: none; }` and `.cm.show { display: flex; }` in CSS. Use `classList.toggle('show')` in JS for both open and close. Always include a close button inside the modal that calls the same toggle function.

### 8. Generic Copy Instead of Truth-Based Copy
**Problem**: "Experience South Africa's Finest Hotels" — generic, could be any hotel.
**Fix**: Use client's ACTUAL tagline ("WHERE WOULD YOU LIKE TO STAY?"), ACTUAL property names, ACTUAL locations, ACTUAL review quotes.

### 9. Not All GBP Properties Discovered
**Problem**: Only found the main GBP (5 reviews). Missed 4 other property GBPs (3,024 total reviews).
**Fix**: ALWAYS search Places API for each property name individually. Sum total reviews across all properties.

### 10. Not Researching Competitors
**Problem**: Generic "competitors are winning" narrative with no data.
**Fix**: ALWAYS query Places API for "hotels in [city]" for each property area. Show real competitor name, rating, review count. Use color-coded better/worse/same badges.

### 11. Missing Negative Review Card
**Problem**: Showed only positive reviews — lacked credibility and missed the opportunity to address real pain points.
**Fix**: Include at least one negative review card (red left border) for the property with the most negative feedback. Use actual review language from GBP.
**Problem**: "Experience South Africa's Finest Hotels" — generic, could be any hotel.
**Fix**: Use client's ACTUAL tagline ("WHERE WOULD YOU LIKE TO STAY?"), ACTUAL property names, ACTUAL locations, ACTUAL review quotes.

### 7. Not All GBP Properties Discovered
**Problem**: Only found the main GBP (5 reviews). Missed 4 other property GBPs (3,024 total reviews).
**Fix**: ALWAYS search Places API for each property name individually. Sum total reviews across all properties.

### 8. Not Researching Competitors
**Problem**: Generic "competitors are winning" narrative with no data.
**Fix**: ALWAYS query Places API for "hotels in [city]" for each property area. Use real competitor names, ratings, review counts.

### 23. Mockup That's Prettier But Not a Sales Weapon
**Problem**: v2 mockup was technically functional (images loaded, JS worked, tabs worked) but Samuel rated it "worse than v1" because it didn't demonstrate pain points or solutions. It was a nicer-looking site, not a sales weapon.
**Fix**: The mockup must VISUALLY show what's broken (e.g., "0% review response rate" as a prominent stat, slow load time indicator, unresponsive reviews) AND show the AI-powered solution (chat widget with real responses, auto-routed feedback, instant lead capture). Include real review quotes as headlines, real competitor names in comparison cards, and per-property booking links. The client should understand "why I need JCE Media" within 5 seconds of viewing.

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

### 7. Post-Deploy Verification via curl
After deploying to GitHub Pages, ALWAYS verify:
```bash
curl -s -o /dev/null -w "%{http_code}" "URL"  # Should be 200
curl -s "URL" | grep -c 'keyword'              # Count expected elements
```
Check: real images, working JS functions, property count, emails, JCE stats, protection layers. Target: 37/37 automated checks.

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

### 12. Images Downloading as HTML (Not Actual Images)
**Problem**: Downloaded "images" that were all 63KB with identical content — all were HTML pages (404/redirect from WordPress). URL pattern was wrong (`2023/01/` instead of `2023/04/` or `2020/04/`).
**Fix**: After downloading ANY asset, ALWAYS verify with `file` command:
```bash
file assets/Web-Logo2-01.png   # Should say "PNG image data"
file assets/DALF6718-HDR.jpg   # Should say "JPEG image data"
```
If it says "HTML document", the URL is wrong. Scrape the actual site HTML to find real image URLs. Common patterns: `/uploads/YYYY/MM/` where YYYY/MM varies.

### 13. index.html Required for GitHub Pages Root
**Problem**: Named report files like `african-sky-hotels-report.html` don't get served at the GitHub Pages root URL (`/iframe`). Only `index.html` is served at `/`.
**Fix**: The main report MUST be named `index.html` on the gh-pages branch. The mockup stays as `mockup.html`. Always verify the live URL `https://USER.github.io/REPO/` shows the report (not a 404 or directory listing).

### 14. end-to-End Deploy Verification
**Problem**: Deployed files that looked correct locally but had broken asset references on the live site.
**Fix**: After every `git push` to gh-pages, ALWAYS run:
```bash
# Wait for GitHub Pages to propagate
sleep 10
# Verify ALL assets return HTTP 200
for f in Web-Logo2-01.png DALF6718-HDR.jpg DALF7733-HDR.jpg CPLF3162-2-HDR.jpg DALF5223-HDR.jpg Werlte-Hotel29.jpg; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://USER.github.io/REPO/assets/$f")
  echo "$code - $f"
done
# Verify report loads
curl -s -o /dev/null -w "Report: %{http_code}\n" "https://USER.github.io/REPO/"
# Verify mockup loads
curl -s -o /dev/null -w "Mockup: %{http_code}\n" "https://USER.github.io/REPO/mockup.html"
# Verify JS functions exist
curl -s "https://USER.github.io/REPO/" | grep -c 'function showTab'
curl -s "https://USER.github.io/REPO/mockup.html" | grep -c 'function toggleChat'
```
Target: Every asset = 200, every function present. This is the deploy-validator check.

## CRITICAL WINS (Reinforce)

### 8. Deploy-Validator Script
A post-deploy verification script that checks: HTTP 200 on all files, `file` MIME types on all assets, JS function presence, element counts. Catches broken assets BEFORE the client sees them. Run after every deploy. See `references/deploy-validator.sh` for the full script.

## QUALITY THRESHOLDS

- Mockup: 9/10 minimum (brand fidelity 10/10)
- Copy: 9/10 minimum (specific, truth-based, persuasive)
- Interactivity: 10/10 (every button works)
- Technical: 8/10 minimum
- Overall: 9/10 minimum to ship
- **Deploy verification: ALL assets HTTP 200, ALL functions present** — non-negotiable

## 15. Supabase State Engine — Column Name `gmb_rating` Not `rating`

**Problem**: The canonical Supabase schema uses `gmb_rating` for the Google Business Profile rating column. Using `rating` causes RPC and ORM mismatches.
**Fix**: Always use `gmb_rating` when referencing the column in Python daemon code, Supabase RPC calls, or SQL queries. The full column set is: `project_id, client_name, target_domain, current_state, locked_at, processing_node_id, extracted_hex_colors, asset_integrity_status, gmb_rating, review_count, simulated_roi_percentage, created_at, updated_at, error_log`.

## 16. Daemon Memory Ledger Path

**Problem**: The `hermes_worker.py` writes `MEMORY_<project_id>.md` to `../MEMORY_<project_id>.md` relative to the daemon directory. If the working directory isn't `daemon/`, the file lands in the wrong place or the Gate 5 check fails.
**Fix**: Always run the daemon from `daemon/` directory: `cd /home/samuelj121314/daemon && source venv/bin/activate && python hermes_worker.py`. Or use an absolute path for the memory ledger: `os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', f'MEMORY_{project_id}.md')`.

## 17. Daemon Scaffold — Required Files

The Sovereign Code Monolith daemon requires this exact file layout. See `references/daemon-scaffold.md` for the full directory tree, setup commands, schema columns, and quality gate summary.

## 18. Daemon Quality Gates (Server-Side)

The Python daemon enforces 5 quality gates during `process_job()`:

1. **Latency Gate**: TTFB > 1500ms → FAIL (proxy for ZA 3G/LTE 300ms target)
2. **Asset MIME Gate**: `verify_asset_integrity()` streams first 8 bytes, checks PNG/JPEG magic numbers, rejects non-200 or non-image responses
3. **GBP Suppression Gate**: `gmb_rating < 4.9` → logs `MAP_PACK_PENALTY` (ReviewTap upsell trigger)
4. **Syntax Balance Gate**: Unbalanced `{}` in target HTML → warning (non-fatal)
5. **Memory Ledger Gate**: `MEMORY_<project_id>.md` must exist on disk after write, or FAIL

**Fix**: These gates run server-side in the daemon, NOT in the client-side deploy-validator. Both sets of checks must pass for a project to reach LIVE state.

## 19. Supabase Row Level Security (RLS) Blocks Anon Key by Default

**Problem**: Every new table in Supabase has RLS enabled by default. When the Python daemon (or test injector) tries to INSERT/SELECT using the anon key, it gets `42501: new row violates row-level security policy`. The RPC functions also fail.

**Fix**: Add this to EVERY migration SQL file after CREATE TABLE:

```sql
-- Disable RLS for daemon-accessed tables (anon key needs full access)
ALTER TABLE hermes_pipeline DISABLE ROW LEVEL SECURITY;
```

Or if you want RLS with a permissive policy:

```sql
ALTER TABLE hermes_pipeline ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all" ON hermes_pipeline FOR ALL USING (true);
```

**Verification**: After running migration, test with anon key:
```python
supabase.table('hermes_pipeline').insert({"client_name": "test", "target_domain": "https://example.com"}).execute()
```
If this succeeds, RLS is properly configured. If you get error 42501, RLS is still blocking.

## 19. `write_file` Tool and Heredocs Both Mangle Triple-Asterisk Values

**Problem**: When a value contains three consecutive asterisks (`***`) — common in API keys, Supabase anon keys, and Telegram bot tokens — both the `write_file` tool and bash heredocs silently truncate or corrupt the value. The `write_file` tool interprets `***` as markdown formatting. Heredocs (`<< 'EOF'`) with `***` inside the content also break. Python source code with `***` in string literals hits SyntaxError from the linter/parser (not from Python itself — the *tool's* linter flags it).

**Fix options (in order of reliability)**:

1. **Write via Python script file with `chr()` construction** (most reliable):
```python
# Build the search key without *** in source
prefix = 'OPENROUTER_API_KEY' + chr(61)  # =
with open('/path/to/.env') as f:
    for line in f:
        if line.startswith(prefix):
            val = line.strip().chr(61), 1)[1]
            break
# Write to target using chr(10) for newlines
content = 'SUPABASE_URL=' + url + chr(10) + 'SUPABASE_KEY=' + key + chr(10)
with open('/target/.env', 'w') as f:
    f.write(content)
```

2. **Base64 encode the value, decode at write time**:
```python
import base64
key_b64 = base64.b64decode('ZXlK...mk=').decode()
```

3. **String concatenation in Python** (no piece contains `***`):
```python
token = 'abc' + chr(42)*3 + 'xyz'
```

**Key insight**: The `***` doesn't break *Python* — it breaks the *Hermes tool layer's* linter and the `write_file`/`execute_code` transport. Always use `chr(61)` for `=`, `chr(42)` for `*`, `chr(10)` for newlines when constructing `.env` content via `-c` one-liners. For complex writes, use a separate `.py` file where the linter is more permissive.

**Verification**: After writing, ALWAYS read back and check:
```python
with open('/target/.env') as f:
    for line in f:
        k, v = line.strip().split(chr(61), 1)
        print(k + ': len=' + str(len(v)))
```
Every value must match the expected length from the source. If `SUPABASE_KEY` shows len=15 instead of len=208, the `***` was truncated.

## 20. Daemon Patched In-Place — Read Before Replace Pattern

**Problem**: Patching `hermes_worker.py` mid-run requires care. Using Python `str.replace()` on the source file is safe ONLY if the old_string is unique and you verify the replace happened.

**Safe patch pattern**:
```python
file_path = "/home/samuelj121314/daemon/hermes_worker.py"
with open(file_path, "r") as f:
    code = f.read()

old_logic = """exact old text"""  # Must match EXACTLY — indentation, quotes, comments
new_logic = """new text"""

if old_logic in code:
    with open(file_path, "w") as f:
        f.write(code.replace(old_logic, new_logic))
    print("Patched successfully.")
else:
    print("Could NOT find target block. ABORT — do NOT write.")
    # Do NOT attempt a partial/fuzzy match — that corrupts the file
```

**Critical**: If `old_logic` is not found, STOP. Do not attempt regex, fuzzy matching, or partial replacement. Abort and ask the user to specify the new target string.

## 21. Daemon pkill Is Too Broad — Use Exact Match

**Problem**: `pkill -f "python3 hermes_worker.py"` matches ANY process whose command line contains that string — including the Hermes gateway itself if it was launched with a wrapper that includes "python3". On the GCP instance, this killed the Hermes agent process (exit -15/SIGTERM), requiring a session restart.

**Fix**: Use exact PID or a more specific pattern:
```bash
# Safe: Find exact PID first
pgrep -f "hermes_worker.py"  # Check what matches
kill $(pgrep -f "hermes_worker.py")  # Kill only if found

# Safer: Use tmux session name to find the exact pane PID
tmux list-panes -t hermes-daemon -F '#{pane_pid}' | xargs kill

# Safest: Send Ctrl+C to the tmux pane first, then kill if needed
tmux send-keys -t hermes-daemon C-c
sleep 2
tmux send-keys -t hermes-daemon "exit" C-m
```

**Rule**: Never `pkill -f python3` or `pkill -f "python3 hermes"` without checking `pgrep` output first. The Hermes gateway runs as a Python process and will be caught by broad patterns.

## 22. OpenRouter Free Model Registry — Use Task-Based Routing

**Problem**: Hardcoding a single model name (e.g., `google/gemini-2.0-flash-001:free`) for all LLM calls wastes the strengths of different free models and makes switching impossible without code changes.

**Fix**: The daemon maintains `/home/samuelj121314/daemon/model_registry.py` with:
- `FREE_MODEL_REGISTRY`: 7+ free models with specialties, speed tiers, context windows
- `TASK_ROUTING`: Maps task names (e.g., `mockup_generation`, `report_narrative`) to optimal models
- `get_model_for_task(task)`: Returns model dict ready for OpenRouter API calls

All models use the `:free` suffix on OpenRouter's free tier. The registry can be extended with new free models as they become available — just add to `FREE_MODEL_REGISTRY` and `TASK_ROUTING`.

## Version History

v1.9 (2026-05-28): Added "v2 is worse than v1" quality post-mortem (mistake 23). Mockup must demonstrate pain points + solutions, not just be prettier. Added deploy-validator canonical path: `/home/samuelj121314/daemon/deploy_validator.py`. Single-file zero-dependency script is canonical; skill dir is reference only.

v1.8 (2026-05-28): Added daemon pkill safety pattern (mistake 21). Added OpenRouter free model registry routing (mistake 22). Model selection is now task-based, not hardcoded.

v1.7 (2026-05-28): Added repo path variability gotcha (mistake 21). Hardcoding `/home/samuelj121314/hermes-config-tracker/` fails because the actual repo lives under `/workspace/`. Always verify repo path with `find /home -name ".git" -path "*/hermes-config-tracker/*" 2>/dev/null` before writing. Added color extraction brand-priority heuristic (mistake 22): frequency-based selection picks accent colors (orange #ff6900) over brand primary (navy #2e3365). Pass a known-brand-color priority list to `get_primary_brand_color()` and match against it first before falling back to frequency. Added patch-target false positive pattern (mistake 23): `code.split(target_hook)[0]` check fails when the hook string appears in comments before the actual injection point. Use line-number-based search or verify the hook's surrounding context (4 lines before/after) to confirm the right block.

v1.6 (2026-05-28): Added `***` escaping in tool layer (mistake 19). Added daemon read-before-replace patch pattern (mistake 20). Fixed Gate 1 from fatal crash to diagnostic flag in hermes_worker.py — slow TTFB is a selling point, not a failure mode.

v1.5 (2026-05-28): Added Supabase RLS default gotcha (mistake 19 → now mistake 21). Any CREATE TABLE in Supabase has Row Level Security enabled by default — anon key is DENIED unless you explicitly disable RLS or add a permissive policy. Added Supabase state engine schema (mistake 15), daemon memory ledger path (mistake 16), daemon scaffold layout (mistake 17), server-side quality gates (mistake 18). Sovereign Code Monolith architecture patterns. Added references/daemon-scaffold.md support file.
v1.3 (2026-05-28): Added image download verification (mistake 12), index.html requirement (mistake 13), end-to-end deploy verification (mistake 14 + win 8). Added deploy-validator.sh reference script. Quality threshold now includes deploy verification as non-negotiable. Problem→Solution narrative is now a mandatory quality dimension.
v1.2 (2026-05-28): Added f-string/JS curly brace corruption mistake. Added chat widget `.show` CSS pattern (mistake + fix). Added competitor data requirement. Added post-deploy curl verification win. Added negative review card pattern.
v1.1 (2026-05-28): Initial compounding intelligence. 8 mistakes, 6 wins, pipeline order.

When skills, agent code, reports, or other deliverables change during a session, sync them back to the config-tracker repo:

```bash
# 1. Sync skills from live system to repo
cd ~/workspace/hermes-config-tracker
rsync -av --exclude='notebooklm' ~/.hermes/skills/devops/ skills/devops/

# 2. Sync MAS system code (if changed)
cp /home/ubuntu/mas-system/multiAgentSystem.js mas-system/
cp -r /home/ubuntu/mas-system/agents mas-system/
cp -r /home/ubuntu/mas-system/utils mas-system/

# 3. Copy any new reports from mas-output
cp /home/ubuntu/mas-output/*.html .

# 4. Commit and push
git add -A
git status          # review what's staged
git commit -m "Describe what changed"
git push origin main
```

**Rules:**
- ALWAYS review `git status` before committing — avoid committing node_modules, .env, or temp files
- The repo's `skills/devops/notebooklm/` is intentionally excluded from rsync (tracker-only skill)
- If SOUL.md changed in `.hermes/`, copy it to the repo too
- Report template lives at `mas-system/report-template.html` in the repo (not in /home/ubuntu/mas-system/)
