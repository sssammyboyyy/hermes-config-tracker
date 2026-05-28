# Reference: African Sky Hotels Audit Report

## File Location
- Local: /home/samuelj121314/mas-output/african-sky-hotels-report.html
- Live: https://sssammyboyyy.github.io/hermes-config-tracker/

## Report Structure
Single self-contained HTML (~27KB) with tabbed nav: Summary | GBP | Website | Mockup | Close Gap

## Key Technical Details
- All CSS/JS inlined (self-contained)
- Mockup embedded via iframe srcdoc (no external file)
- 6 protection layers on all pages
- Tab switching: CSS display:none/.active toggled by JS

## Data Sources
- GBP: Google Places API (New) places:searchText endpoint
- Website: curl-based extraction (no browser)
- Mockup: Inline HTML with real brand data from GBP

## Deployment (GitHub Pages)
cp report.html /tmp/gh-pages-deploy/index.html
cd /tmp/gh-pages-deploy
git init && git checkout -b gh-pages
git add index.html && git commit -m "Deploy"
git push -u origin gh-pages --force

## Key Pitfalls
1. Netlify CLI OOMs on e2-micro — use GitHub Pages
2. write_file truncates large HTML — use Python for >20KB
3. patch truncates — verify closing tags after
4. Puppeteer deleted in cleanup — use curl + APIs
5. Places API doesn't return business responses — response_rate = 0 expected
