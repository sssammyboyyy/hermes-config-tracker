# Deployment Pattern — GitHub Pages

## Correct Pattern (Confirmed Working)

1. Copy report to `/tmp/gh-pages-deploy/index.html`
2. Copy mockup to `/tmp/gh-pages-deploy/mockup.html` (separate file, NOT embedded as srcdoc)
3. `cd /tmp/gh-pages-deploy && git init && git checkout -b gh-pages`
4. `git add -A && git commit -m "message"`
5. `git push -u origin gh-pages --force`
6. Wait 3-5 seconds, verify with curl

## Pitfalls
- Netlify CLI OOMs on e2-micro — use GitHub Pages
- Don't embed mockup as base64 srcdoc in report — regex replacement corrupts the file
- JS function names must match between definition and onclick handlers
- write_file truncates files >20KB — use Python for large files