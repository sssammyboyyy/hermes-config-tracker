# Deploy Validator — Post-Deploy Verification Script

Run this ENTIRE checklist after every `git push` to github-pages. Nothing ships until all checks pass.

## Pre-Deploy (Local)

```bash
# 1. Verify all assets are actual images (not HTML pages)
for f in assets/*; do
  mime=$(file --mime-type -b "$f")
  if [[ "$mime" != image/* ]]; then
    echo "FAIL: $(basename $f) has MIME type '$mime' — expected image/*"
    exit 1
  fi
done
echo "PASS: All assets are valid images"

# 2. Verify JS syntax (balanced braces)
for f in index.html mockup.html; do
  open=$(grep -o '{' "$f" | wc -l)
  close=$(grep -o '}' "$f" | wc -l)
  [ "$open" != "$close" ] && echo "FAIL: $f has unbalanced braces" && exit 1
done
echo "PASS: JS braces balanced"
```

## Post-Deploy (Live)

```bash
sleep 10
BASE="https://USER.github.io/REPO"

# 1. All assets HTTP 200
for f in Web-Logo2-01.png DALF6718-HDR.jpg DALF7733-HDR.jpg CPLF3162-2-HDR.jpg DALF5223-HDR.jpg Werlte-Hotel29.jpg; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/assets/$f")
  [ "$code" != "200" ] && echo "FAIL: $f returned HTTP $code" && exit 1
done
echo "PASS: All assets HTTP 200"

# 2. Pages load
curl -s -o /dev/null -w "Report: %{http_code}\n" "$BASE/"
curl -s -o /dev/null -w "Mockup: %{http_code}\n" "$BASE/mockup.html"

# 3. JS functions present
for fn in showTab calcReportROI speakSummary; do
  count=$(curl -s "$BASE/" | grep -c "function $fn")
  [ "$count" -eq 0 ] && echo "FAIL: $fn() missing" && exit 1
done
for fn in calcROI toggleChat chatReply; do
  count=$(curl -s "$BASE/mockup.html" | grep -c "function $fn")
  [ "$count" -eq 0 ] && echo "FAIL: $fn() missing" && exit 1
done
echo "PASS: All JS functions present"

# 4. Assets are images
mime=$(curl -s "$BASE/assets/Web-Logo2-01.png" | file --mime-type -b -)
[[ "$mime" != "image/png" ]] && echo "FAIL: logo is $mime" && exit 1
echo "PASS: Assets verified as images"

echo "=== ALL DEPLOY CHECKS PASSED ==="
```

## Failure Recovery

| Check Fails | Fix |
|---|---|
| Asset is HTML page | Scrape live site HTML for correct image URLs. Try multiple `/uploads/YYYY/MM/` patterns. |
| Asset HTTP 404 | File not in gh-pages branch. Copy and push again. |
| JS function missing | Verify function name matches between definition and onclick handlers. |
| Unbalanced braces | Hand-edit JS in HTML file. |
