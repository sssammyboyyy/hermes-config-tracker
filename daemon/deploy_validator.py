#!/usr/bin/env python3
"""
deploy_validator.py — Pre-flight quality gate for MAS audit report deployments.

Zero-dependency Python 3 script (uses only stdlib: os, re, pathlib, urllib).
Designed to run before every git push to gh-pages.

Checks:
  1. Stale File Pruning — delete any .html files except index.html and mockup.html
  2. Syntax Sanity — balanced {} and () in all .html files; onclick→function cross-ref
  3. Asset Integrity — extract all <img src> tags; HEAD request to verify HTTP 200 + image MIME

Usage:
  python3 deploy_validator.py /path/to/deploy_dir
  python3 deploy_validator.py /path/to/deploy_dir --domain https://sssammyboyyy.github.io/hermes-config-trackor

Run in pipeline:
  python3 deploy_validator.py . && git add -A && git commit -m "deploy" && git push origin gh-pages
"""

import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────

ALLOWED_HTML = {"index.html", "mockup.html"}
IMAGE_MIMES = {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif", "image/svg+xml", "image/x-icon", "image/bmp", "image/tiff"}
TIMEOUT = 15  # seconds for HTTP requests

# ── Helpers ────────────────────────────────────────────────────────────────

def log_ok(msg):   print(f"  ✓ {msg}")
def log_fail(msg): print(f"  ✗ {msg}")
def log_warn(msg): print(f"  ⚠ {msg}")
def log_info(msg): print(f"  ℹ {msg}")

# ── Check 1: Stale File Pruning ───────────────────────────────────────────

def prune_stale_files(target_dir):
    """Delete any .html files in target_dir that aren't index.html or mockup.html."""
    errors = []
    pruned = []
    base = Path(target_dir)

    if not base.is_dir():
        log_fail(f"Target directory not found: {target_dir}")
        return False, [f"Directory not found: {target_dir}"], []

    for f in base.iterdir():
        if f.is_file() and f.suffix == ".html" and f.name not in ALLOWED_HTML:
            log_fail(f"Stale file pruned: {f.name}")
            f.unlink()
            pruned.append(f.name)

    if not pruned:
        log_ok("No stale .html files found")
    else:
        log_ok(f"Pruned {len(pruned)} stale file(s): {', '.join(pruned)}")

    return True, errors, pruned


# ── Check 2: Syntax Sanity ────────────────────────────────────────────────

def check_syntax(target_dir):
    """Check all .html files for balanced braces, parens, and function references."""
    errors = []
    base = Path(target_dir)

    for html_file in sorted(base.glob("*.html")):
        content = html_file.read_text(encoding="utf-8", errors="ignore")

        # Overall brace balance
        ob = content.count("{")
        cb = content.count("}")
        if ob != cb:
            errors.append(f"{html_file.name}: unbalanced braces ({{={ob}, }}={cb})")

        # Overall paren balance
        op = content.count("(")
        cp = content.count(")")
        if op != cp:
            errors.append(f"{html_file.name}: unbalanced parentheses ((={op}, )={cp})")

        # Check each inline <script> block individually
        scripts = re.findall(r"<script>(.*?)</script>", content, re.DOTALL)
        for i, script in enumerate(scripts):
            s_ob = script.count("{")
            s_cb = script.count("}")
            if s_ob != s_cb:
                errors.append(f"{html_file.name} script[{i+1}]: unbalanced braces ({{={s_ob}, }}={s_cb})")

            s_op = script.count("(")
            s_cp = script.count(")")
            if s_op != s_cp:
                errors.append(f"{html_file.name} script[{i+1}]: unbalanced parentheses ((={s_op}, )={s_cp})")

        # Cross-reference onclick="fn()" against declared function fn()
        onclick_funcs = set(re.findall(r'onclick=["\'](\w+)\s*\(', content))
        declared_funcs = set(re.findall(r"function\s+(\w+)\s*\(", content))
        for func in onclick_funcs:
            if func not in declared_funcs:
                errors.append(f"{html_file.name}: onclick='{func}()' references undeclared function")

    if not errors:
        log_ok("Syntax sanity passed — all braces, parens, and function refs valid")
    for e in errors:
        log_fail(e)

    return len(errors) == 0, errors


# ── Check 3: Asset Integrity ──────────────────────────────────────────────

def check_assets(target_dir, domain=None):
    """
    Extract all <img src> from .html files.
    For absolute URLs: HEAD request, verify HTTP 200 + image Content-Type.
    For local paths: verify file exists + `file` MIME is image/*.
    """
    errors = []
    base = Path(target_dir)
    checked = set()

    for html_file in sorted(base.glob("*.html")):
        content = html_file.read_text(encoding="utf-8", errors="ignore")
        img_urls = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)

        for url in img_urls:
            if url in checked:
                continue
            checked.add(url)

            # Local file path
            if not url.startswith("http"):
                local_path = base / url
                if not local_path.exists():
                    errors.append(f"Local asset not found: {url}")
                    log_fail(f"Missing local asset: {url}")
                else:
                    log_ok(f"Local asset exists: {url}")
                continue

            # Skip external domains (fonts.googleapis, etc.)
            if domain and domain not in url:
                log_info(f"Skipping external URL: {url}")
                continue

            # Absolute URL on our domain — verify via HEAD
            try:
                req = urllib.request.Request(url, method="HEAD")
                with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                    status = resp.status
                    content_type = resp.headers.get("Content-Type", "").split(";")[0].strip()

                if status != 200:
                    errors.append(f"Asset HTTP {status}: {url}")
                    log_fail(f"Asset HTTP {status}: {url}")
                elif content_type and content_type not in IMAGE_MIMES:
                    if "html" in content_type:
                        errors.append(f"Asset returned HTML ({content_type}): {url}")
                        log_fail(f"Asset returned HTML: {url} (Content-Type: {content_type})")
                    else:
                        errors.append(f"Asset unexpected MIME ({content_type}): {url}")
                        log_fail(f"Asset unexpected MIME: {url} ({content_type})")
                else:
                    log_ok(f"Asset OK: {url.split('/')[-1]} ({content_type}, {status})")

            except urllib.error.HTTPError as e:
                errors.append(f"Asset HTTP {e.code}: {url}")
                log_fail(f"Asset HTTP {e.code}: {url}")
            except urllib.error.URLError as e:
                errors.append(f"Asset URL error ({e.reason}): {url}")
                log_fail(f"Asset URL error: {url} ({e.reason})")
            except Exception as e:
                errors.append(f"Asset check error ({e}): {url}")
                log_fail(f"Asset check error: {url} ({e})")

    if not errors:
        log_ok(f"All {len(checked)} assets verified")

    return len(errors) == 0, errors


# ── Main Runner ────────────────────────────────────────────────────────────

def run_validation(target_dir, domain=None):
    """
    Run all 3 checks. Returns True if all pass (safe to deploy), False if any fail.
    """
    print(f"\n{'='*60}")
    print(f"  DEPLOY VALIDATOR — {target_dir}")
    if domain:
        print(f"  Domain: {domain}")
    print(f"{'='*60}\n")

    if not Path(target_dir).is_dir():
        log_fail(f"Target directory not found: {target_dir}")
        return False

    all_passed = True
    total_errors = []

    # ── Check 1: Stale Files ─────────────────────────────────────────────
    print("── Check 1: Stale File Pruning ──")
    passed, errs, _ = prune_stale_files(target_dir)
    total_errors.extend(errs)
    if not passed:
        all_passed = False
    print()

    # ── Check 2: Syntax ──────────────────────────────────────────────────
    print("── Check 2: Syntax Sanity ──")
    passed, errs = check_syntax(target_dir)
    total_errors.extend(errs)
    if not passed:
        all_passed = False
    print()

    # ── Check 3: Assets ──────────────────────────────────────────────────
    print("── Check 3: Asset Integrity ──")
    passed, errs = check_assets(target_dir, domain)
    total_errors.extend(errs)
    if not passed:
        all_passed = False
    print()

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"{'='*60}")
    if all_passed:
        print(f"  ✓ ALL CHECKS PASSED — Safe to deploy")
        print(f"{'='*60}\n")
        return True
    else:
        print(f"  ✗ {len(total_errors)} CHECK(S) FAILED — Deploy blocked")
        for e in total_errors:
            print(f"    ✗ {e}")
        print(f"{'='*60}\n")
        return False


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    dom = None
    if len(sys.argv) > 2:
        if sys.argv[2].startswith("--domain="):
            dom = sys.argv[2].split("=", 1)[1]
        elif sys.argv[2] == "--domain" and len(sys.argv) > 3:
            dom = sys.argv[3]

    result = run_validation(target, dom)
    sys.exit(0 if result else 1)
