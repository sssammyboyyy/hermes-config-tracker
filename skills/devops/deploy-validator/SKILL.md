---
name: deploy-validator
description: Pre-deploy quality gate — validates asset integrity, stale files, and syntax before any git commit/push to gh-pages. Run before every deploy.
triggers:
  - "deploy"
  - "validate"
  - "pre-deploy"
  - "before push"
  - "ship"
  - "release"
---

# Deploy Validator

## Purpose
Programmatic pre-deploy quality gate that runs **before** any `git push` to `gh-pages`. Blocks deployment if any check fails. Prevents broken assets, stale files, and syntax errors from reaching the client.

## Checks
1. **Asset Integrity** — Parse all `.html` for `<img src>` tags. For each:
   - Local file → `file --mime-type` must return `image/*`
   - Remote URL → HTTP 200 + `Content-Type: image/*` (catches HTML pages masquerading as images)
2. **Stale File Pruning** — Destination must only contain `index.html`, `mockup.html`, `assets/`. Auto-deletes orphaned `.html` from previous runs.
3. **Syntax Sanity** — All `.html` files checked for balanced `{}` and `()`. Inline `<script>` blocks checked individually. Cross-references `onclick="fn()"` against declared `function fn()`.

## Usage

```bash
# Canonical validator (zero-dependency, stdlib only):
python3 /home/samuelj121314/daemon/deploy_validator.py /path/to/deploy_dir

# With live URL verification:
python3 /home/samuelj121314/daemon/deploy_validator.py /path/to/deploy_dir --domain=https://sssammyboyyy.github.io/hermes-config-tracker

# From the deploy directory (gh-pages checkout):
cd /home/samuelj121314/workspace/hermes-config-tracker && git checkout gh-pages
python3 /home/samuelj121314/daemon/deploy_validator.py .
```

This skill directory contains the reference implementation. The **canonical** validator is the single-file daemon script at `/home/samuelj121314/daemon/deploy_validator.py` — always use that one.

## Integration with Pipeline

Deploy validator runs as **Step 3** in the MAS audit pipeline:

```
Research → GBP Scrape → Website Audit → Mockup → Report Assembly
    → [1] write_report.py
    → [2] write_mockup.py
    → [3] deploy-validator.py  ← HERE (blocks if any check fails)
    → [4] git add/commit/push to gh-pages
    → [5] Post-deploy live verification (--live)
```

Exit code 0 = safe to push. Exit code 1 = **deploy blocked**, fix errors and re-run.
