# Brand Asset Extraction Guide

How to extract real brand assets from a client's website for use in mockups.

## Method: curl + regex (no browser needed)

### Step 1: Fetch the homepage HTML
```bash
curl -s --max-time 20 -L \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  "https://www.example.com" > /tmp/site_page.html
```

### Step 2: Extract logo
```python
# Look for img tags with "logo" in src or class
logos = re.findall(r'<img[^>]*src="([^"]*(?:logo|Logo|LOGO)[^"]*)"', html, re.IGNORECASE)
# Also check CSS background-image references
logos += re.findall(r'url\([^)]*(?:logo|Logo|LOGO)[^)]*\)', html, re.IGNORECASE)
```

### Step 3: Extract hero/images
```python
# All image URLs
images = re.findall(r'(?:src|href|url)\s*[=\(]\s*["\']?(https?://[^"\'>\s]+\.(?:png|jpg|jpeg|gif|webp|svg)[^"\'>\s]*)', html, re.IGNORECASE)
# WordPress lazy-loading
lazy = re.findall(r'data-src="([^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"', html, re.IGNORECASE)
```

### Step 4: Extract brand colors
```bash
# Fetch the main CSS file
curl -s "https://www.example.com/wp-content/themes/THEME/style.css" > /tmp/theme.css
# Then extract hex colors and count frequency
# Most common non-white/non-black colors = brand palette
```
```python
colors = re.findall(r'#[0-9a-fA-F]{6}', css)
from collections import Counter
primary = Counter(colors).most_common(10)
```

### Step 5: Extract fonts
```python
fonts = re.findall(r'font-family:\s*([^;]+)', html + css)
# Look for Google Fonts links
gfonts = re.findall(r'fonts\.googleapis\.com/css2\?family=([^"]+)', html)
```

### Step 6: Download assets to local dir
```bash
mkdir -p /tmp/site_assets
curl -s -o /tmp/site_assets/logo.png "$LOGO_URL"
curl -s -o /tmp/site_assets/hero1.jpg "$HERO1_URL"
# etc.
```

### Step 7: Upload to GitHub Pages for mockup to reference
```bash
# Copy assets to gh-pages deploy dir
cp -r /tmp/site_assets /tmp/gh-pages-deploy/assets

# Read HTML files and rewrite image URLs to GitHub Pages URLs
# Replace: https://www.example.com/wp-content/uploads/2020/04/logo.png
# With:    https://USER.github.io/REPO/assets/logo.png
```

### Step 8: Verify accessibility
```bash
curl -s -o /dev/null -w "%{http_code}" "https://USER.github.io/REPO/assets/logo.png"
# Should return 200 after ~3s GitHub Pages propagation delay
```

## African Sky Hotels (confirmed working)
- **Logo**: `https://www.africanskyhotels.com/wp-content/uploads/2020/04/Web-Logo2-01.png`
- **Hero images**: DALF6718-HDR.jpg, DALF7733-HDR.jpg, CPLF3162-2-HDR.jpg, DALF5223-HDR.jpg, Werlte-Hotel29.jpg
- **Colors**: #2e3365 (navy), #31cdcf (teal), #ff6900 (accent orange), #cb3524 (red), #3a3a3a (dark gray)
- **Fonts**: Montserrat (headings), Open Sans (body) — both Google Fonts
- **Theme**: Divi (WordPress)
- **Slider**: Smart Slider 3

## Key Lesson
**NEVER use emoji placeholders in the mockup.** Always use real images or no image at all. Emoji placeholders make the mockup look amateurish and signal that the work was automated without care.


**PITFALL: Regex-based image extraction has limits** — you're parsing HTML with regex, so complex nested structures will miss images. Use this method for the initial pass, then manually verify the extracted assets. If the site loads content via JavaScript (React, Vue), you'll only get server-rendered images — which is usually sufficient for the homepage hero and logo.
