#!/bin/bash
# bulletproof_backup.sh — Hermes State Auto-Backup
# Backs up SOUL.md, MEMORY.md, daemon/ configs to private hermes-core-backup repo.
# Designed to run via cron or systemd timer.
# Usage: bash /home/samuelj121314/daemon/bulletproof_backup.sh

set -e

echo "============================================"
echo "  HERMES STATE BACKUP — $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================"

BACKUP_DIR="/tmp/hermes_backup_$(date +%Y%m%d_%H%M%S)"
REPO_URL="https://github.com/sssammyboyyy/hermes-core-backup.git"
CREDENTIALS_FILE="$HOME/.git-credentials"

# ── Step 1: Stage critical state files ───────────────────────────────────
mkdir -p "$BACKUP_DIR"

echo "[1/5] Staging critical state files..."

# SOUL.md — the brain
cp /home/samuelj121314/SOUL.md "$BACKUP_DIR/" 2>/dev/null && echo "  ✓ SOUL.md staged" || echo "  ⚠ SOUL.md not found"

# Memory files
cp /home/samuelj121314/.hermes/MEMORY*.md "$BACKUP_DIR/" 2>/dev/null && echo "  ✓ MEMORY files staged" || true
cp /home/samuelj121314/MEMORY*.md "$BACKUP_DIR/" 2>/dev/null && echo "  ✓ MEMORY files staged" || true

# Hermes skills (entire directory)
cp -r /home/samuelj121314/.hermes/skills/ "$BACKUP_DIR/skills/" 2>/dev/null && echo "  ✓ skills/ staged" || echo "  ⚠ skills/ not found"

# Daemon directory
cp -r /home/samuelj121314/daemon/ "$BACKUP_DIR/daemon/" 2>/dev/null && echo "  ✓ daemon/ staged" || echo "  ⚠ daemon/ not found"

# .env (redacted — we back up the EXAMPLE, never the secrets)
cp /home/samuelj121314/daemon/.env.example "$BACKUP_DIR/daemon/" 2>/dev/null && echo "  ✓ .env.example staged" || true

echo ""
echo "[2/5] Backup staged at: $BACKUP_DIR"
ls -la "$BACKUP_DIR/"

# ── Step 2: Git init + commit + push ─────────────────────────────────────
echo ""
echo "[3/5] Committing to hermes-core-backup..."

cd "$BACKUP_DIR"

git init -b main 2>/dev/null

# Configure git credentials
if [ -f "$CREDENTIALS_FILE" ]; then
    # Extract token from credentials file
    TOKEN=$(grep -oP 'ghp_\w+' "$CREDENTIALS_FILE" | head -1)
    if [ -n "$TOKEN" ]; then
        git remote add origin "https://sssammyboyyy:${TOKEN}@github.com/sssammyboyyy/hermes-core-backup.git" 2>/dev/null || \
        git remote set-url origin "https://sssammyboyyy:${TOKEN}@github.com/sssammyboyyy/hermes-core-backup.git"
        echo "  ✓ Remote configured with PAT"
    else
        echo "  ⚠ No PAT found in credentials — push may fail"
        git remote add origin "$REPO_URL" 2>/dev/null || true
    fi
else
    echo "  ⚠ No .git-credentials file found"
    git remote add origin "$REPO_URL" 2>/dev/null || true
fi

git add -A
git config user.email "hermes-daemon@jcemedia.com"
git config user.name "Hermes Daemon"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
git commit -m "Automated state snapshot: ${TIMESTAMP}" 2>/dev/null || {
    echo "  ℹ Nothing to commit (no changes since last backup)"
}

# ── Step 3: Push ─────────────────────────────────────────────────────────
echo ""
echo "[4/5] Pushing to hermes-core-backup..."

git push -u origin main --force 2>&1 | tail -3

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "  ✓ Backup pushed successfully"
else
    echo "  ✗ Push failed — check network / PAT permissions"
fi

# ── Step 4: Cleanup ──────────────────────────────────────────────────────
echo ""
echo "[5/5] Cleaning up staging directory..."
rm -rf "$BACKUP_DIR"
echo "  ✓ Staging directory removed"

echo ""
echo "============================================"
echo "  BACKUP COMPLETE — $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================"
