# GitHub Repo Bloat Cleanup

## Problem
A git repo accumulates history bloat over time — old commits with large files, unused directories, etc. Even deleting files in a new commit keeps them in `.git` history.

## Solution: Nuclear Reset (Single Clean Commit)

When the repo has accumulated too much history bloat and you want a fresh start:

```bash
# 1. Back up what you want to keep to /tmp
cp -r /path/to/repo/essential-files /tmp/backup

# 2. Delete .git (removes ALL history)
rm -rf /path/to/repo/.git

# 3. Clean out everything else
cd /path/to/repo
find . -maxdepth 1 -not -name '.' -not -name '.git' -exec rm -rf {} +

# 4. Restore essential files from backup
cp -r /tmp/backup/* .

# 5. Reinit git
git init
git remote add origin https://<user>:***@github.com/<user>/<repo>.git
git config user.email "hermes@mas.local"
git config user.name "Hermes MAS"

# 6. Commit and force-push to overwrite remote history
git add -A
git commit -m "Lean init: essential files only"
git push -u origin main --force
```

## Reconstructing Remote URL from .git-credentials

If you deleted `.git` and need the remote URL, it's stored in `~/.git-credentials`:

```bash
cat ~/.git-credentials
# Format: https://<user>:***@github.com
```

Extract user and token, then build: `https://<user>:***@github.com/<user>/<repo>.git`

## Dealing with Branch Name Mismatch

If the remote has `main` but git init creates `master`:

```bash
# Force push master to main on remote
git push origin master:main --force

# Delete the extra branch on remote
git push origin --delete master

# Rename local to main
git branch -m master main

# Set upstream
git push -u origin main
```

## When to Use This
- Repo has grown large from accumulated commits with large files
- You want to reduce disk usage and clone time
- The repo is a config tracker / backup (not a collaborative dev repo)
- You have a backup of the essential files elsewhere

## When NOT to Use This
- Collaborative repos with shared history
- Repos with meaningful commit history you want to preserve
- Any repo where others depend on the history
