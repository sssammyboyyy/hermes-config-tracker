# Puppeteer / Chromium Cache Management

## Disk Space Overview

| Location | Typical Size | Safe to Delete? |
|----------|-------------|-----------------|
| `~/.cache/puppeteer/` | 1.0–1.5 GB | **YES** — will reinstall on demand |
| `~/.hermes/node/lib/node_modules/puppeteer` | 20–45 MB | **YES** — will reinstall on demand |
| `~/.hermes/hermes-agent/` (venv, TUI, etc.) | ~1 GB | **NO** — this is the Hermes runtime |

## Clearing Puppeteer Cache

```bash
# Check size first
du -sh ~/.cache/puppeteer/

# Delete Chromium cache (safe — Puppeteer redownloads on next use)
rm -rf ~/.cache/puppeteer/

# Check node_modules puppeteer size
du -sh ~/.hermes/node/lib/node_modules/puppeteer/

# Delete puppeteer node_modules
rm -rf ~/.hermes/node/lib/node_modules/puppeteer/
```

## After Deletion

Puppeteer will automatically download Chromium again when:
- A skill calls `mcp_puppeteer_puppeteer_navigate`
- A script calls `puppeteer.launch()`

First run after deletion takes longer (download time). Subsequent runs use the cache.

## Skill Library Cleanup

The `.hermes/skills/` directory accumulates skill categories over time:
- Check with: `du -sh ~/.hermes/skills/` and `ls ~/.hermes/skills/`
- Delete unused categories: `rm -rf ~/.hermes/skills/<category>/`
- Keep: only the skill categories relevant to current work

Current MAS-relevant skills (keep these):
- `devops/` — marketing-audit, gbp-scraper, website-auditor, mockup-generator, usage-guardian, hermes-config
