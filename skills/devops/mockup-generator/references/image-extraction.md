# Image Extraction — JavaScript Snippet for Puppeteer

The JS below is designed to be passed to `mcp_puppeteer_puppeteer_evaluate(script=...)`.
It extracts all brand-relevant images from the current page.

```javascript
(function() {
    var images = [];
    var seen = {};
    
    // 1. All img tags (skip tiny icons, data URIs)
    document.querySelectorAll('img').forEach(function(img) {
        if (img.src && !img.src.startsWith('data:') && img.width > 50) {
            var key = img.src;
            if (!seen[key]) {
                seen[key] = true;
                images.push({
                    src: img.src,
                    alt: img.alt || '',
                    width: img.naturalWidth || img.width,
                    height: img.naturalHeight || img.height,
                    type: 'img'
                });
            }
        }
    });
    
    // 2. Background images in key brand areas
    var heroEls = document.querySelectorAll(
        'header, .hero, .banner, [class*="logo"], [class*="hero"], [id*="logo"], [class*="brand"]'
    );
    heroEls.forEach(function(el) {
        var bg = window.getComputedStyle(el).backgroundImage;
        if (bg && bg !== 'none') {
            var match = bg.match(/url\(["']?(.*?)["']?\)/);
            if (match && !seen[match[1]]) {
                seen[match[1]] = true;
                images.push({ src: match[1], type: 'bg', from: el.tagName + '.' + el.className });
            }
        }
    });
    
    // 3. Logo links (common pattern: <a> wrapping <img> or <svg>)
    document.querySelectorAll('a[href="/"] img, a[href="./"] img').forEach(function(img) {
        if (img.src && !seen[img.src]) {
            seen[img.src] = true;
            images.push({
                src: img.src,
                alt: img.alt || 'logo',
                width: img.naturalWidth || img.width,
                height: img.naturalHeight || img.height,
                type: 'logo'
            });
        }
    });
    
    // 4. Sort by pixel area (largest first — likely heroes and logos)
    images.sort(function(a, b) {
        return (b.width * b.height) - (a.width * a.height);
    });
    
    // Return top 10
    return images.slice(0, 10);
})()
```

## Image Download Pattern (Python)

After extracting URLs, download with `urllib.request`:

```python
import urllib.request, os
from urllib.parse import urlparse

def download_image(img_url, output_path, base_url):
    """Download image, resolving relative URLs."""
    if img_url.startswith('/'):
        parsed = urlparse(base_url)
        img_url = f"{parsed.scheme}://{parsed.netloc}{img_url}"
    elif not img_url.startswith('http'):
        img_url = base_url.rstrip('/') + '/' + img_url.lstrip('/')
    
    # Determine extension
    ext = 'png' if '.png' in img_url.lower() else 'jpg'
    path = f"{output_path}.{ext}"
    
    try:
        urllib.request.urlretrieve(img_url, path)
        return path
    except Exception as e:
        return None  # Skip failed downloads gracefully
```

## Categorization Heuristic

After extraction:
- `type: 'logo'` → definitely the logo
- First image with `width > 800` → likely the hero image
- Next 2-4 large images → content/product images
- Skip: icons (width < 100), tracking pixels, social media icons

## Pitfalls

1. **Relative URLs**: Always resolve against site origin before downloading
2. **Lazy loading**: `data-src` may hold the real URL; check if `src` is a placeholder (1px gif, blur hash)
3. **CORS**: Some sites block cross-origin image loading; if download fails, reference by original URL
4. **SVG logos**: May be inline SVGs (no `src`); extract the SVG element's outer HTML and embed directly
