#!/usr/bin/env python3
"""
deploy-validator.py — Pre-deploy validation gate for MAS audit reports.

Runs 3 checks BEFORE allowing git commit/push to gh-pages:
  1. Asset Integrity — all <img src> URLs return 200 + valid image MIME
  2. Stale File Pruning — destination only has index.html, mockup.html, assets/
  3. Syntax Sanity — all HTML/JS has balanced braces and parentheses

Usage:
  python3 scripts/deploy-validator.py [--dir <path>] [--live <url>]

Exit code 0 = all checks pass (safe to deploy)
Exit code 1 = checks failed (blocked from deploy)
"""

import argparse, os, re, subprocess, sys, time
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────

ALLOWED_HTML_FILES = {'index.html', 'mockup.html'}
ALLOWED_DIRS = {'assets', 'mas-system', 'research', 'memory', 'skills', '.git'}
ALLOWED_EXTENSIONS = {'.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.md', '.json', '.txt', '.sh', '.py', '.svg', '.webp', '.gif', '.ico'}
IMAGE_MIME_PREFIXES = ('image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/gif', 'image/svg+xml', 'image/x-icon')

# ANSI colours
R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
B = '\033[94m'
C = '\033[0m'

def log(msg, colour=G): print(f"{colour}  ✓ {msg}{C}")
def warn(msg): print(f"{Y}  ⚠ {msg}{C}")
def fail(msg): print(f"{R}  ✗ {msg}{C}")
def info(msg): print(f"{B}  ℹ {msg}{C}")

# ── Check 1: Asset Integrity ──────────────────────────────────────────────

def check_asset_integrity(base_dir, live_url=None):
    """
    Parse all .html files in base_dir for <img src> tags.
    For each URL:
      - If local file exists → verify it's a real image via `file --mime-type`
      - If remote URL → curl to verify HTTP 200 + valid Content-Type
    Returns (passed: bool, errors: list)
    """
    errors = []
    checked = set()
    html_files = list(Path(base_dir).glob('*.html'))
    
    if not html_files:
        fail("No .html files found in deploy directory")
        return False, ["No HTML files found"]
    
    for html_path in html_files:
        content = html_path.read_text(encoding='utf-8', errors='ignore')
        # Extract all img src values
        img_urls = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
        # Also check iframe src
        iframe_urls = re.findall(r'<iframe[^>]+src=["\']([^"\']+)["\']', content)
        
        all_urls = img_urls  # images are the critical ones
        
        for url in all_urls:
            if url in checked:
                continue
            checked.add(url)
            
            # Determine if local or remote
            if url.startswith('http'):
                # Remote URL — curl it
                if live_url and not url.startswith(live_url):
                    info(f"Skipping external URL: {url}")
                    continue
                    
                try:
                    result = subprocess.run(
                        ['curl', '-sI', '--max-time', '15', url],
                        capture_output=True, text=True, timeout=20
                    )
                    headers = result.stdout.lower()
                    
                    # Check HTTP 200
                    if '200 ok' not in headers and 'http/2 200' not in headers and 'http/1.1 200' not in headers:
                        # Try a full GET to be sure
                        result2 = subprocess.run(
                            ['curl', '-s', '--max-time', '15', '-o', '/dev/null', '-w', '%{http_code}|%{content_type}', url],
                            capture_output=True, text=True, timeout=20
                        )
                        parts = result2.stdout.strip().split('|')
                        http_code = parts[0] if parts else '000'
                        content_type = parts[1] if len(parts) > 1 else ''
                        
                        if http_code != '200':
                            errors.append(f"Asset HTTP {http_code}: {url}")
                            continue
                    else:
                        content_type = ''
                        for line in headers.split('\n'):
                            if 'content-type:' in line:
                                content_type = line.split(':', 1)[1].strip()
                                break
                    
                    # If we got headers via HEAD, check content type
                    if '200 ok' in headers or 'http/2 200' in headers or 'http/1.1 200' in headers:
                        content_type = ''
                        for line in headers.split('\n'):
                            if 'content-type:' in line:
                                content_type = line.split(':', 1)[1].strip()
                                break
                        
                        if content_type and not any(content_type.startswith(p) for p in IMAGE_MIME_PREFIXES):
                            if 'html' in content_type:
                                errors.append(f"Asset returned HTML not image: {url} (Content-Type: {content_type})")
                            else:
                                errors.append(f"Asset has unexpected MIME type: {url} (Content-Type: {content_type})")
                            continue
                    
                    log(f"Asset OK: {url.split('/')[-1]}")
                    
                except subprocess.TimeoutExpired:
                    errors.append(f"Asset timeout: {url}")
                except Exception as e:
                    errors.append(f"Asset check error: {url} → {e}")
                    
            elif url.startswith('//'):
                # Protocol-relative URL — skip or resolve
                info(f"Protocol-relative URL (skipping head check): {url}")
                
            elif url.startswith('/') or url.startswith('./'):
                # Absolute/local path — resolve relative to base_dir
                local_path = Path(base_dir) / url.lstrip('./').lstrip('/')
                if not local_path.exists():
                    errors.append(f"Local asset not found: {local_path}")
                else:
                    try:
                        result = subprocess.run(
                            ['file', '--mime-type', '-b', str(local_path)],
                            capture_output=True, text=True, timeout=5
                        )
                        mime = result.stdout.strip()
                        if not any(mime.startswith(p) for p in IMAGE_MIME_PREFIXES):
                            errors.append(f"Local asset is not an image: {local_path} (MIME: {mime})")
                        else:
                            log(f"Local asset OK: {local_path.name} ({mime})")
                    except Exception as e:
                        errors.append(f"Local asset check error: {local_path} → {e}")
            else:
                # Relative path like "assets/foo.jpg"
                local_path = Path(base_dir) / url
                if not local_path.exists():
                    errors.append(f"Local asset not found: {local_path}")
                else:
                    try:
                        result = subprocess.run(
                            ['file', '--mime-type', '-b', str(local_path)],
                            capture_output=True, text=True, timeout=5
                        )
                        mime = result.stdout.strip()
                        if not any(mime.startswith(p) for p in IMAGE_MIME_PREFIXES):
                            errors.append(f"Local asset is not an image: {local_path} (MIME: {mime})")
                        else:
                            log(f"Local asset OK: {local_path.name} ({mime})")
                    except Exception as e:
                        errors.append(f"Local asset check error: {local_path} → {e}")
    
    return len(errors) == 0, errors


# ── Check 2: Stale File Pruning ───────────────────────────────────────────

def check_stale_files(base_dir, auto_prune=False):
    """
    Ensure base_dir only contains:
      - index.html, mockup.html (allowed HTML)
      - assets/ directory
      - Other allowed non-HTML files (.css, .js at root are ok)
    Delete any orphaned .html files from previous audit runs.
    Returns (passed: bool, errors: list, pruned: list)
    """
    errors = []
    pruned = []
    base = Path(base_dir)
    
    if not base.is_dir():
        fail(f"Deploy directory not found: {base_dir}")
        return False, [f"Directory not found: {base_dir}"], []
    
    stale_files = []
    for item in base.iterdir():
        if item.is_file():
            if item.suffix == '.html' and item.name not in ALLOWED_HTML_FILES:
                stale_files.append(item)
        elif item.is_dir() and item.name not in ALLOWED_DIRS:
            # Unexpected directories — warn but don't auto-delete
            warn(f"Unexpected directory: {item.name}/ (review manually)")
    
    if stale_files:
        for f in stale_files:
            msg = f"Stale file detected: {f.name}"
            if auto_prune:
                f.unlink()
                pruned.append(f.name)
                info(f"Auto-pruned: {f.name}")
            else:
                errors.append(msg)
                fail(msg)
    else:
        log("No stale files detected")
    
    return len(errors) == 0, errors, pruned


# ── Check 3: Syntax Sanity ────────────────────────────────────────────────

def check_syntax_sanity(base_dir):
    """
    Check all .html files for balanced braces {} and parentheses ().
    Inline <script> content is extracted and checked separately.
    Returns (passed: bool, errors: list)
    """
    errors = []
    html_files = list(Path(base_dir).glob('*.html'))
    
    for html_path in html_files:
        content = html_path.read_text(encoding='utf-8', errors='ignore')
        
        # Check overall braces in file
        open_b = content.count('{')
        close_b = content.count('}')
        if open_b != close_b:
            errors.append(f"{html_path.name}: unbalanced braces ({open_b} open, {close_b} close)")
        
        # Check overall parens
        open_p = content.count('(')
        close_p = content.count(')')
        if open_p != close_p:
            errors.append(f"{html_path.name}: unbalanced parentheses ({open_p} open, {close_p} close)")
        
        # Check inline <script> blocks individually
        scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
        for i, script in enumerate(scripts):
            s_open_b = script.count('{')
            s_close_b = script.count('}')
            if s_open_b != s_close_b:
                errors.append(f"{html_path.name} script[{i+1}]: unbalanced braces ({s_open_b}/{s_close_b})")
            
            s_open_p = script.count('(')
            s_close_p = script.count(')')
            if s_open_p != s_close_p:
                errors.append(f"{html_path.name} script[{i+1}]: unbalanced parens ({s_open_p}/{s_close_p})")
        
        # Check that referenced JS functions exist in the file
        # Extract all onclick="functionName(...)" handlers
        onclick_funcs = re.findall(r'onclick=["\'](\w+)\s*\([^)]*\)', content)
        # Extract all function declarations
        declared_funcs = set(re.findall(r'function\s+(\w+)\s*\(', content))
        
        for func in onclick_funcs:
            if func not in declared_funcs and func not in ('return',):
                errors.append(f"{html_path.name}: onclick references '{func}()' but function not declared in file")
    
    return len(errors) == 0, errors


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='MAS Deploy Validator — pre-deploy quality gate')
    parser.add_argument('--dir', default='.', help='Deploy directory to validate (default: current dir)')
    parser.add_argument('--live', default=None, help='Live URL to verify remote assets (e.g. https://user.github.io/repo)')
    parser.add_argument('--prune', action='store_true', help='Auto-prune stale files instead of just reporting')
    parser.add_argument('--assets-only', action='store_true', help='Only run asset integrity check')
    parser.add_argument('--stale-only', action='store_true', help='Only run stale file check')
    parser.add_argument('--syntax-only', action='store_true', help='Only run syntax check')
    args = parser.parse_args()
    
    base_dir = os.path.abspath(args.dir)
    
    print(f"\n{'='*60}")
    print(f"  MAS DEPLOY VALIDATOR")
    print(f"  Directory: {base_dir}")
    if args.live:
        print(f"  Live URL:  {args.live}")
    print(f"{'='*60}\n")
    
    run_all = not (args.assets_only or args.stale_only or args.syntax_only)
    total_errors = []
    
    # ── Check 1: Asset Integrity ──────────────────────────────────────────
    if run_all or args.assets_only:
        print(f"{B}━━━ Check 1: Asset Integrity ━━━{C}")
        passed, errors = check_asset_integrity(base_dir, args.live)
        total_errors.extend(errors)
        if passed:
            print(f"{G}  PASSED: All assets valid{C}\n")
        else:
            print(f"{R}  FAILED: {len(errors)} asset error(s){C}\n")
    
    # ── Check 2: Stale File Pruning ───────────────────────────────────────
    if run_all or args.stale_only:
        print(f"{B}━━━ Check 2: Stale File Pruning ━━━{C}")
        passed, errors, pruned = check_stale_files(base_dir, args.prune)
        total_errors.extend(errors)
        if passed:
            msg = "PASSED: No stale files"
            if pruned:
                msg += f" (auto-pruned: {', '.join(pruned)})"
            print(f"{G}  {msg}{C}\n")
        else:
            print(f"{R}  FAILED: {len(errors)} stale file(s){C}\n")
    
    # ── Check 3: Syntax Sanity ────────────────────────────────────────────
    if run_all or args.syntax_only:
        print(f"{B}━━━ Check 3: Syntax Sanity ━━━{C}")
        passed, errors = check_syntax_sanity(base_dir)
        total_errors.extend(errors)
        if passed:
            print(f"{G}  PASSED: All syntax checks OK{C}\n")
        else:
            print(f"{R}  FAILED: {len(errors)} syntax error(s){C}\n")
    
    # ── Summary ───────────────────────────────────────────────────────────
    print(f"{'='*60}")
    if not total_errors:
        print(f"{G}  ALL CHECKS PASSED — Safe to deploy{C}")
        print(f"{'='*60}\n")
        sys.exit(0)
    else:
        print(f"{R}  {len(total_errors)} CHECK(S) FAILED — Deploy blocked{C}")
        for e in total_errors:
            print(f"{R}    ✗ {e}{C}")
        print(f"{'='*60}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
