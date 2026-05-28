# Quality Checklist — Concrete Tests

Run these checks before every deployment.

## Mockup
- [ ] Real logo image (not text) — assets/logo.png referenced
- [ ] Real hero/property images (not emoji) — image files in assets/
- [ ] Brand colors match client CSS hex values
- [ ] Brand fonts loaded via Google Fonts link
- [ ] Phone clickable (tel: link)
- [ ] Real Google reviews visible
- [ ] Mobile responsive (375px)
- [ ] All 6 protection layers

## Report
- [ ] Nav tabs work — click each, section appears
- [ ] JS function names consistent — def matches onclick
- [ ] GBP shows real data (not N/A)
- [ ] All gap cards present
- [ ] JCE stats: 416%, 65%, 8.5x, $15M+
- [ ] Mockup iframe src=URL (not srcdoc)
- [ ] Direct mockup link resolves

## Deploy
- [ ] GitHub Pages 200 on all URLs (wait 5s after push)
- [ ] Assets 200 (logo, images)
- [ ] All HTTPS (no mixed content)

## JS Console (zero errors)
- TypeError → DOM ID mismatch
- 404 → Wrong asset path
