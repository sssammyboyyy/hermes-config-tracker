#!/bin/bash
# deploy-hook.sh — Git pre-push hook for gh-pages branch
# Install: cp this file to .git/hooks/pre-push in the gh-pages working tree
#
# This hook runs the deploy-validator before every push to gh-pages.
# If checks fail, the push is BLOCKED.

set -e

DEPLOY_DIR="$(git rev-parse --show-toplevel)"
VALIDATOR="$HOME/.hermes/skills/devops/deploy-validator/scripts/deploy-validator.py"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  MAS DEPLOY VALIDATOR — Pre-Push Hook  ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Check current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "gh-pages" ]; then
    echo "  Branch is '$branch' — validator only runs on gh-pages. Skipping."
    exit 0
fi

# Run the validator
python3 "$VALIDATOR" --dir "$DEPLOY_DIR" --prune
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "  ✗ PUSH BLOCKED — Fix errors above and try again."
    echo ""
    exit 1
fi

echo ""
echo "  ✓ Validator passed — proceeding with push."
echo ""
exit 0
